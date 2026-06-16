import sys
import os
import pytest
from datetime import datetime, timezone

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'orchestrator_api'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import yaml
from engine.detector import analyze_message, build_matches, compute_score, fuzzy_hits, find_phrase_hits
from engine.normalizers import normalize_text, normalize_leetspeak_basic, normalize_arabic
from engine.crypto_heuristics import crypto_signals, shannon_entropy, looks_base64
from engine.correlator import risk_level_from_score, aggregate_by_user
from engine.models import MessageResult, Match, UserAggregate


@pytest.fixture
def es_rules():
    rules_path = os.path.join(os.path.dirname(__file__), '..', 'rules', 'es.yaml')
    with open(rules_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


@pytest.fixture
def en_rules():
    rules_path = os.path.join(os.path.dirname(__file__), '..', 'rules', 'en.yaml')
    with open(rules_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


class TestDetector:
    def test_high_risk_spanish(self, es_rules):
        result = analyze_message(
            message_id='test-001',
            user_id='hash_user1',
            text='voy a atentar contra el edificio con una bomba casera, celula durmiente activada',
            lang='es',
            lang_cfg=es_rules,
            timestamp=datetime.now(timezone.utc)
        )
        assert result.risk_score > 12
        assert result.risk_level == "high"
        assert len(result.matches) > 0

    def test_low_risk_spanish(self, es_rules):
        result = analyze_message(
            message_id='test-002',
            user_id='hash_user2',
            text='hola buen dia como estas',
            lang='es',
            lang_cfg=es_rules,
            timestamp=datetime.now(timezone.utc)
        )
        assert result.risk_score < 5
        assert result.risk_level == "low"

    def test_high_risk_english(self, en_rules):
        result = analyze_message(
            message_id='test-003',
            user_id='hash_user3',
            text='death to the west, join the jihad, suicide vest planned',
            lang='en',
            lang_cfg=en_rules,
            timestamp=datetime.now(timezone.utc)
        )
        assert result.risk_score > 12
        assert result.risk_level == "high"

    def test_crypto_detection(self, es_rules):
        result = analyze_message(
            message_id='test-004',
            user_id='hash_user4',
            text='clave de acceso: SGVsbG8gV29ybGQgZnJvbSB0aGUgT1NJTlQ=',
            lang='es',
            lang_cfg=es_rules,
            timestamp=datetime.now(timezone.utc)
        )
        assert result.crypto_signals["score"] > 0
        assert len(result.crypto_signals["b64_candidates"]) > 0

    def test_euphemism_detection(self, es_rules):
        result = analyze_message(
            message_id='test-005',
            user_id='hash_user5',
            text='trae el paquete a la boda',
            lang='es',
            lang_cfg=es_rules,
            timestamp=datetime.now(timezone.utc)
        )
        assert result.risk_score > 0
        match_kinds = [m.kind for m in result.matches]
        assert "euphemism" in match_kinds

    def test_behavioral_markers(self, es_rules):
        result = analyze_message(
            message_id='test-006',
            user_id='hash_user6',
            text='hablame por privado, unete al grupo, solo gente seria',
            lang='es',
            lang_cfg=es_rules,
            timestamp=datetime.now(timezone.utc)
        )
        assert result.risk_score > 0
        match_kinds = [m.kind for m in result.matches]
        assert "behavior" in match_kinds

    def test_empty_text(self, es_rules):
        result = analyze_message(
            message_id='test-007',
            user_id='hash_user7',
            text='',
            lang='es',
            lang_cfg=es_rules,
            timestamp=datetime.now(timezone.utc)
        )
        assert result.risk_score == 0
        assert result.risk_level == "low"

    def test_yaml_format_consistency(self, es_rules, en_rules):
        for rules in [es_rules, en_rules]:
            phr = rules.get("phrases_high_risk", {})
            assert "items" in phr, f"phrases_high_risk missing 'items' in {rules.get('language')}"
            assert "weight" in phr, f"phrases_high_risk missing 'weight' in {rules.get('language')}"


class TestNormalizers:
    def test_leetspeak_basic(self):
        assert "bomb" in normalize_leetspeak_basic("b0mb")
        assert "attack" in normalize_leetspeak_basic("@tt@ck")
        assert "site" in normalize_leetspeak_basic("s1te")

    def test_normalize_common(self):
        from engine.normalizers import normalize_common
        result = normalize_common("  HELLO   WORLD  ")
        assert result == "hello world"

    def test_arabic_normalization(self):
        text = "إأآا"
        result = normalize_arabic(text, {"normalize_alef": True})
        assert result == "اااا"


class TestCryptoHeuristics:
    def test_shannon_entropy(self):
        assert shannon_entropy("") == 0.0
        assert shannon_entropy("aaaa") == 0.0
        assert shannon_entropy("abcd") > 1.5

    def test_base64_detection(self):
        assert looks_base64("SGVsbG8gV29ybGQ=") == True
        assert looks_base64("not-base64!!!") == False

    def test_crypto_signals(self):
        text = "token: SGVsbG8gV29ybGQgZnJvbSB0aGUgT1NJTlQ= hex: 0x1234567890abcdef1234567890abcdef"
        signals = crypto_signals(text)
        assert signals["score"] > 0
        assert len(signals["b64_candidates"]) > 0
        assert len(signals["hex_candidates"]) > 0


class TestCorrelator:
    def test_risk_levels(self):
        assert risk_level_from_score(0) == "low"
        assert risk_level_from_score(7) == "low"
        assert risk_level_from_score(8) == "medium"
        assert risk_level_from_score(11) == "medium"
        assert risk_level_from_score(12) == "high"
        assert risk_level_from_score(100) == "high"

    def test_aggregate_by_user(self):
        results = [
            MessageResult(
                message_id="1", user_id="user1", language="es",
                raw_text="test1", normalized_text="test1",
                timestamp=datetime(2024, 1, 1, 10, 0),
                risk_score=5.0, risk_level="low",
                matches=[Match(kind="keyword", value="bomb", score=5.0)],
                crypto_signals={}, notes=[]
            ),
            MessageResult(
                message_id="2", user_id="user1", language="es",
                raw_text="test2", normalized_text="test2",
                timestamp=datetime(2024, 1, 1, 11, 0),
                risk_score=15.0, risk_level="high",
                matches=[Match(kind="phrase_high", value="atentar", score=15.0)],
                crypto_signals={}, notes=[]
            ),
        ]
        aggs = aggregate_by_user(results)
        assert len(aggs) == 1
        assert aggs[0].user_id == "user1"
        assert aggs[0].total_messages == 2
        assert aggs[0].peak_risk == 15.0
        assert aggs[0].cumulative_risk == 20.0


class TestSchemas:
    def test_message_create_valid(self):
        from schemas import MessageCreate
        msg = MessageCreate(
            message_id="123",
            chat_id="456",
            user_handle_hash="abc",
            text="test",
            timestamp=datetime.now(timezone.utc)
        )
        assert msg.message_id == "123"

    def test_message_create_text_limit(self):
        from schemas import MessageCreate
        with pytest.raises(Exception):
            MessageCreate(
                message_id="123",
                chat_id="456",
                user_handle_hash="abc",
                text="x" * 20000,
                timestamp=datetime.now(timezone.utc)
            )

    def test_case_update_valid_status(self):
        from schemas import CaseUpdate
        for status in ["open", "analyzing", "analyzed", "closed", "error"]:
            update = CaseUpdate(status=status)
            assert update.status == status

    def test_case_update_invalid_status(self):
        from schemas import CaseUpdate
        with pytest.raises(Exception):
            CaseUpdate(status="invalid_status")
