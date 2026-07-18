from src.models.project import Module, Integration
from src.utils.naming import camel_to_words
from src.i18n import t


class LLMEnhancer:
    def __init__(self, enabled: bool = False, api_key: str = "", locale: str = "zh"):
        self.enabled = enabled
        self.api_key = api_key
        self.locale = locale
        self._client = None

        if enabled and api_key:
            try:
                import anthropic
                self._client = anthropic.Anthropic(api_key=api_key)
            except Exception:
                self._client = None

    def enhance_endpoint_name(self, method_name: str) -> str:
        if not self._client:
            return camel_to_words(method_name)

        try:
            response = self._client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=50,
                messages=[{
                    "role": "user",
                    "content": t("llm.enhance_endpoint", self.locale, method_name=method_name),
                }],
            )
            return response.content[0].text.strip()
        except Exception:
            return camel_to_words(method_name)

    def enhance_module_description(self, module: Module) -> str:
        if not self._client:
            return t("llm.fallback_module_desc", self.locale, name=module.name)

        try:
            classes = module.controllers + module.services
            response = self._client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=100,
                messages=[{
                    "role": "user",
                    "content": t("llm.enhance_module", self.locale, module_name=module.name, classes=", ".join(classes)),
                }],
            )
            return response.content[0].text.strip()
        except Exception:
            return t("llm.fallback_module_desc", self.locale, name=module.name)

    def enhance_integration_description(self, integration: Integration) -> str:
        if not self._client:
            return t("llm.fallback_integration_desc", self.locale,
                     source=integration.source_module,
                     type=integration.integration_type.value,
                     target=integration.target_module)

        try:
            response = self._client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=100,
                messages=[{
                    "role": "user",
                    "content": t("llm.enhance_integration", self.locale,
                                 source=integration.source_module,
                                 target=integration.target_module,
                                 type=integration.integration_type.value,
                                 interface=integration.interface_name,
                                 methods=", ".join(integration.methods)),
                }],
            )
            return response.content[0].text.strip()
        except Exception:
            return t("llm.fallback_integration_desc", self.locale,
                     source=integration.source_module,
                     type=integration.integration_type.value,
                     target=integration.target_module)
