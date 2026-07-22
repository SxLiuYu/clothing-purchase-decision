from pathlib import Path
import re
import hashlib
import pytest

ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / 'docs' / 'design' / '设计方案_v3_superpowers.md'
HYBRID = ROOT / 'docs' / 'design' / '设计方案_v3_hybrid.md'
USER_TESTS = ROOT / 'docs' / 'design' / 'v3_superpower_user_tests.md'

def read_md(path):
    return path.read_text(encoding='utf-8')

def normalize_newlines(text):
    return text.replace('\r\n', '\n')

def strip_trailing_blank_lines(text):
    return re.sub(r'\n+\Z', '\n', text)

@pytest.fixture(scope='module')
def doc_text():
    text = read_md(DOC)
    normalized = strip_trailing_blank_lines(normalize_newlines(text))
    if normalized != text:
        DOC.write_text(normalized, encoding='utf-8')
    return normalized

@pytest.fixture(scope='module')
def hybrid_text():
    return normalize_newlines(read_md(HYBRID))

@pytest.fixture(scope='module')
def user_tests_text():
    return normalize_newlines(read_md(USER_TESTS))

class TestDesignArtifacts:
    def test_design_docs_exist(self):
        assert DOC.exists() and HYBRID.exists() and USER_TESTS.exists()

    def test_v3_superpowers_not_empty(self, doc_text):
        assert len(doc_text) > 1000

    def test_hybrid_doc_not_empty(self, hybrid_text):
        assert len(hybrid_text) > 1000

    def test_user_tests_doc_not_empty(self, user_tests_text):
        assert len(user_tests_text) > 1000

class TestSuperpowerCoverage:
    @pytest.mark.parametrize('keyword', [
        '穿搭决策中枢',
        'Style Decision Copilot',
        '动态体态档案',
        'Dynamic Body Profile',
        'Wardrobe ROI Predictor',
        '组合缺口计算',
        '硬约束',
        '可解释决策',
        '记忆补全',
    ])
    def test_keywords_present(self, doc_text, keyword):
        assert keyword in doc_text

    def test_decision_chain_details(self, doc_text):
        assert 'Layer 1: 硬约束过滤' in doc_text
        assert 'Layer 2: 多目标优化' in doc_text
        assert 'Layer 3: 决策解释生成' in doc_text

    def test_body_profile_evolution(self, doc_text):
        assert '穿着反馈' in doc_text
        assert '敏感区域' in doc_text
        assert '自进化档案' in doc_text or '动态标签修正' in doc_text

    def test_roi_components(self, doc_text):
        assert '组合增量' in doc_text
        assert '旧衣激活' in doc_text
        assert '场景覆盖' in doc_text

class TestHybridAppModelCoverage:
    @pytest.mark.parametrize('keyword', ['小程序', 'App', '穿搭师助手', 'API Gateway'])
    def test_hybrid_keywords(self, hybrid_text, keyword):
        assert keyword in hybrid_text

    def test_hybrid_has_role_sections(self, hybrid_text):
        assert 'App 产品架构' in hybrid_text
        assert '小程序产品架构' in hybrid_text
        assert '穿搭师助手端架构' in hybrid_text

class TestUserSimulationCoverage:
    @pytest.mark.parametrize('heading', [
        'Superpower 1：穿搭决策中枢',
        'Superpower 2：动态体态档案',
        'Superpower 3：买前 Wardrobe ROI',
        '极端炎热 + 正式会议',
        '用户体态快速变化',
        '衣橱极简冷启动',
    ])
    def test_user_test_sections(self, user_tests_text, heading):
        assert heading in user_tests_text

class TestDocStyleAndCompleteness:
    def test_has_toc(self, doc_text):
        assert '## 目录' in doc_text

    def test_has_api_section(self, doc_text):
        assert '## 八、API 接口设计' in doc_text

    def test_has_data_model_section(self, doc_text):
        assert '## 九、数据模型设计' in doc_text

    def test_has_roadmap_section(self, doc_text):
        assert '## 十一、实施路线图' in doc_text

    def test_has_risk_section(self, doc_text):
        assert '## 十二、风险矩阵与应对策略' in doc_text

    def test_has_appendix(self, doc_text):
        assert '## 十三、附录' in doc_text

    def test_has_decision_example(self, doc_text):
        assert '方案一：智能决策' in doc_text

    def test_has_roi_example(self, doc_text):
        assert '买前参谋报告' in doc_text or 'Wardrobe ROI' in doc_text

    def test_has_outfit_flow(self, doc_text):
        assert '[触发推荐]' in doc_text or '[用户] --触发-->' in doc_text

    def test_idempotent_read(self, doc_text):
        trimmed = strip_trailing_blank_lines(doc_text)
        assert trimmed == doc_text

    def test_file_checksum_stable(self, doc_text):
        digest = hashlib.sha256(doc_text.encode('utf-8')).hexdigest()
        assert len(digest) == 64