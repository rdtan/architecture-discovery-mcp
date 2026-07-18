import pytest
from src.i18n import t, get_headers, TRANSLATIONS, HEADER_KEYS


def test_t_returns_chinese_by_default():
    assert t("val.built") == "已建"
    assert t("val.yes") == "是"
    assert t("val.no") == "否"


def test_t_returns_english():
    assert t("val.built", "en") == "Built"
    assert t("val.yes", "en") == "Yes"
    assert t("val.no", "en") == "No"


def test_t_with_format_kwargs():
    assert t("val.param", "zh", param="id") == "参数: id"
    assert t("val.param", "en", param="id") == "Parameter: id"


def test_t_with_name_kwarg():
    assert "ruoyi" in t("pptx.arch_diagram", "zh", name="ruoyi")
    assert "ruoyi" in t("pptx.arch_diagram", "en", name="ruoyi")
    assert "Application Architecture" in t("pptx.arch_diagram", "en", name="ruoyi")


def test_t_unknown_key_returns_key():
    assert t("nonexistent.key") == "nonexistent.key"
    assert t("nonexistent.key", "en") == "nonexistent.key"


def test_t_unknown_locale_falls_back_to_zh():
    assert t("val.built", "fr") == "已建"


def test_get_headers_zh():
    headers = get_headers("aa01")
    assert len(headers) == 9
    assert headers[0] == "应用域编号"
    assert headers[-1] == "建设现状"


def test_get_headers_en():
    headers = get_headers("aa01", "en")
    assert len(headers) == 9
    assert headers[0] == "Domain ID"
    assert headers[-1] == "Build Status"


def test_get_headers_all_sheets():
    for sheet_id in HEADER_KEYS:
        zh = get_headers(sheet_id, "zh")
        en = get_headers(sheet_id, "en")
        assert len(zh) == len(en), f"Header count mismatch for {sheet_id}"
        assert all(h != "" for h in zh), f"Empty zh header in {sheet_id}"
        assert all(h != "" for h in en), f"Empty en header in {sheet_id}"


def test_get_headers_unknown_sheet():
    assert get_headers("nonexistent") == []


def test_all_translations_have_both_locales():
    for key, entry in TRANSLATIONS.items():
        assert "zh" in entry, f"Missing zh for key: {key}"
        assert "en" in entry, f"Missing en for key: {key}"
