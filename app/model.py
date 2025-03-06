from transformers import AutoModelForCausalLM, AutoTokenizer
from transformers import LlamaTokenizer


class LlModel:
    MODEL_NAME = "yandex/YandexGPT-5-Lite-8B-pretrain"

    def __init__(self):
        self.tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME, legacy=False)
        self.model = AutoModelForCausalLM.from_pretrained(
            MODEL_NAME,
            device_map="cuda",
            torch_dtype="auto",
        )

    def generate(self, input: str) -> str:
        input_ids = self.tokenizer(input, return_tensors="pt").to("cuda")
        outputs = self.model.generate(**input_ids, max_new_tokens=10)
        return self.tokenizer.decode(outputs[0], skip_special_tokens=True)


if __name__ == "__main__":
    # m = LlModel()
    # m.generate("Привет, расскажи о себе")
    MODEL_NAME = "yandex/YandexGPT-5-Lite-8B-pretrain"

    tokenizer = LlamaTokenizer.from_pretrained(MODEL_NAME)
    model = AutoModelForCausalLM.from_pretrained(
        MODEL_NAME,
        device_map="cuda",
        torch_dtype="auto",
    )

    input_text = "Кто сказал тебе, что нет на свете настоящей,"
    input_ids = tokenizer(input_text, return_tensors="pt").to("cuda")

    outputs = model.generate(**input_ids, max_new_tokens=10)
    print(tokenizer.decode(outputs[0], skip_special_tokens=True))
