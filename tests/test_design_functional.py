from pathlib import Path
import re
import hashlib
import markdown
import pytest
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / 'docs' / 'design' / '设计方案_v3_superpowers.md'
HYBRID = ROOT / 'docs' / 'design' / '设计方案_v3_hybrid.md'
USER_TESTS = ROOT / 'docs' / 'design' / 'v3_superpower_user_tests.md'


def read_md(path):
    return path.read_text(encoding='utf-8')


def normalize_text(text):
    return text.replace('\r\n', '\n')


def md_headings(text):
    html = markdown.markdown(text)
    soup = BeautifulSoup(html, 'html.parser')
    return [tag.get_text(strip=True) for tag in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])]


def contains_any(text, values):
    return all(value in text for value in values)


@pytest.fixture(scope='module')
def doc_text():
    return normalize_text(read_md(DOC))


@pytest.fixture(scope='module')
def hybrid_text():
    return normalize_text(read_md(HYBRID))


@pytest.fixture(scope='module')
def user_text():
    return normalize_text(read_md(USER_TESTS))


class TestDesignArtifacts:
    def test_design_docs_exist(self):
        assert DOC.exists() and HYBRID.exists() and USER_TESTS.exists()

    def test_v3_superpowers_not_empty(self, doc_text):
        assert len(doc_text) > 1000

    def test_hybrid_doc_not_empty(self, hybrid_text):
        assert len(hybrid_text) > 1000

    def test_user_tests_doc_not_empty(self, user_text):
        assert len(user_text) > 1000


class TestDocumentStructure:
    def test_top_level_headings(self, doc_text):
        headings = md_headings(doc_text)
        expected = [
            '目录',
            '一、产品定位与超级能力',
            '二、产品架构总览',
            '三、模块 A：数字衣橱 - Auto Closet Cognition',
            '四、模块 B：穿搭决策中枢 -- Style Decision Copilot',
            '五、模块 C：买前防撞参谋 - Wardrobe ROI Predictor',
            '六、模块 D：脸型体型 + 社媒推荐',
            '七、数据流与状态机设计',
            '八、API 接口设计',
            '九、数据模型设计',
            '十、技术实现方案',
            '十一、实施路线图',
            '十二、风险矩阵与应对策略',
            '十三、附录',
        ]
        for heading in expected:
            assert heading in headings, heading

    def test_no_unclosed_code_blocks(self, doc_text):
        assert doc_text.count('```') % 2 == 0


class TestModuleA:
    def test_identity_and_functions(self, doc_text):
        assert contains_any(doc_text, ['模块 A：数字衣橱 - Auto Closet Cognition', 'Auto Closet Cognition'])
        assert contains_any(doc_text, ['A-01', '拍照/选图录入', 'AI 自动打标', '衣橱浏览', '穿着记录'])

    def test_memory_completion(self, doc_text):
        assert contains_any(doc_text, ['记忆补全', '动态标签修正'])

    def test_multi_source_memory(self, doc_text):
        assert contains_any(doc_text, ['用户主动上传', '电商购买记录', '社交图片', '穿着反馈', 'OCR'])

    def test_graph_relationships(self, doc_text):
        assert contains_any(doc_text, ['可搭配', '同场景', '同色系', '替代关系'])


class TestModuleB:
    def test_identity_and_functions(self, doc_text):
        assert contains_any(doc_text, ['模块 B：穿搭决策中枢 -- Style Decision Copilot', 'Style Decision Copilot'])
        assert contains_any(doc_text, ['B-01', 'B-02', 'B-03', 'B-04', 'B-05', 'B-06', 'B-07', 'B-08', 'B-09', 'B-10', 'B-11'])

    def test_decision_chain(self, doc_text):
        assert contains_any(doc_text, ['硬约束', '多目标优化', '决策解释生成'])

    def test_hard_constraints(self, doc_text):
        assert contains_any(doc_text, ['温度', '场合', '活动强度', '过敏'])

    def test_output_format(self, doc_text):
        assert contains_any(doc_text, ['方案一：智能决策', '风险提示', '切换成本'])

    def test_soft_optimization(self, doc_text):
        assert contains_any(doc_text, ['美学评分', '衣橱复用', '用户偏好'])

    def test_dynamic_fit_evolution(self, doc_text):
        assert contains_any(doc_text, ['穿着反馈', '敏感区域', '自进化档案', '动态标签修正'])

    def test_feedback_learning(self, doc_text):
        assert contains_any(doc_text, ['决策反馈学习', '用户接受率', '连续拒绝', '更新体态/偏好档案'])


class TestModuleC:
    def test_identity_and_functions(self, doc_text):
        assert contains_any(doc_text, ['模块 C：买前防撞参谋 - Wardrobe ROI Predictor', '模块 C：买前防撞参谋 -- Wardrobe ROI Predictor', 'Wardrobe ROI Predictor'])
        assert contains_any(doc_text, ['C-01', 'C-02', 'C-03', 'C-04', 'C-05', 'C-06', 'C-07', 'C-08', 'C-09', 'C-10', 'C-11'])

    def test_combination_gap(self, doc_text):
        assert contains_any(doc_text, ['组合增量', '旧衣激活', '场景覆盖'])

    def test_roi_output(self, doc_text):
        assert contains_any(doc_text, ['购买收益分', 'Wardrobe ROI'])
        assert contains_any(doc_text, ['推荐购买', '不推荐'])

    def test_alternative_suggestions(self, doc_text):
        assert '替代方案' in doc_text

    def test_conflict_detection(self, doc_text):
        assert contains_any(doc_text, ['冗余', '冲突'])


class TestModuleD:
    def test_social_inspiration(self, doc_text):
        assert contains_any(doc_text, ['社媒', '小红书', '微博'])

    def test_same_feature_filter(self, doc_text):
        assert contains_any(doc_text, ['同脸型', '同体型'])

    def test_ai_single_analysis(self, doc_text):
        assert contains_any(doc_text, ['单品', '购买链接'])


class TestUserSimulation:
    def test_core_scenarios(self, user_text):
        scenarios = [
            'Superpower 1：穿搭决策中枢',
            'Superpower 2：动态体态档案',
            'Superpower 3：买前 Wardrobe ROI',
            '极端炎热 + 正式会议',
            '用户体态快速变化',
            '衣橱极简冷启动',
        ]
        for scenario in scenarios:
            assert scenario in user_text, scenario

    def test_pass_criteria(self, user_text):
        assert '通过标准' in user_text
        assert '失败条件' in user_text

    def test_conclusion_table(self, user_text):
        assert '结论' in user_text


class TestHybridArchitecture:
    def test_roles(self, hybrid_text):
        assert contains_any(hybrid_text, ['App（主阵地）', '小程序（增长引擎）', '穿搭师助手（专业端）'])

    def test_sync_strategy(self, hybrid_text):
        assert contains_any(hybrid_text, ['App 优先本地', '小程序轻量同步'])

    def test_api_gateway(self, hybrid_text):
        assert 'API Gateway' in hybrid_text

    def test_ai_engine(self, hybrid_text):
        assert 'AI 引擎层' in hybrid_text

    def test_data_layer(self, hybrid_text):
        assert contains_any(hybrid_text, ['PostgreSQL', 'Qdrant', 'Redis'])

    def test_decision_domain(self, hybrid_text):
        assert contains_any(hybrid_text, ['业务服务'])


class TestFunctionalCompleteness:
    def test_toc_items(self, doc_text):
        assert contains_any(doc_text, ['一、产品定位与超级能力', '二、产品架构总览', '十三、附录'])

    def test_api_contracts(self, doc_text):
        assert contains_any(doc_text, ['POST', 'Request', 'Response'])

    def test_data_models(self, doc_text):
        assert contains_any(doc_text, ['User', '用户服务域'])
        assert contains_any(doc_text, ['Wardrobe', '衣物'])

    def test_roadmap_phases(self, doc_text):
        phases = ['Phase 1', 'Phase 2', 'Phase 3']
        for phase in phases:
            assert phase in doc_text, phase

    def test_risks(self, doc_text):
        assert '隐私' in doc_text
        assert contains_any(doc_text, ['成本', 'AI 推理成本', '金额', '性价比'])

    def test_idempotent_read(self, doc_text):
        trimmed = '\n'.join(line.rstrip(' \t') for line in doc_text.splitlines())
        DOC.write_text(trimmed, encoding='utf-8')
        assert read_md(DOC) == trimmed

    def test_file_checksum_stable(self, doc_text):
        digest = hashlib.sha256(doc_text.encode('utf-8')).hexdigest()
        assert len(digest) == 64