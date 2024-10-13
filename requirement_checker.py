from transformers import RobertaTokenizer, RobertaModel
import torch
import os
import re

class RequirementChecker:
    def __init__(self, regulation_manager):
        self.regulation_manager = regulation_manager
        self.tokenizer = RobertaTokenizer.from_pretrained("roberta-base")
        self.model = RobertaModel.from_pretrained("roberta-base")
        self.results_dir = r"C:\Users\user\Documents\hack\hack\saved_results"

        if not os.path.exists(self.results_dir):
            os.makedirs(self.results_dir)

    def preprocess_text(self, text):
        text = text.lower()
        text = re.sub(r'[^\w\s]', '', text)  # Удаление знаков препинания
        return text

    def check_requirements(self, requirements, file_name):
        results = []
        saved_file_path = os.path.join(self.results_dir, file_name + "_results.txt")

        if os.path.exists(saved_file_path):
            with open(saved_file_path, "r") as saved_file:
                saved_results = saved_file.read()
            return saved_results

        regulations = self.regulation_manager.get_regulations()

        for requirement in requirements:
            status = "не проверено"
            comments = []

            extracted_elements = self.extract_elements(requirement)

            req_input = self.tokenizer(requirement, return_tensors='pt', truncation=True, max_length=512)

            for reg_name, reg_content in regulations.items():
                reg_input = self.tokenizer(reg_content, return_tensors='pt', truncation=True, max_length=512)

                with torch.no_grad():
                    req_embedding = self.model(**req_input).last_hidden_state.mean(dim=1)
                    reg_embedding = self.model(**reg_input).last_hidden_state.mean(dim=1)

                similarity = torch.nn.functional.cosine_similarity(req_embedding, reg_embedding).item()

                if similarity > 0.9:
                    status = "соответствует"
                    comments.append(f"Совпадение с регламентом {reg_name} (схожесть: {similarity:.2f})")

            if not comments:
                comments.append("Совпадений не найдено")

            results.append({
                "requirement": extracted_elements,
                "status": status,
                "comments": "; ".join(comments)
            })

        with open(saved_file_path, "w") as saved_file:
            for result in results:
                saved_file.write(f"Требование: {result['requirement']}\n")
                saved_file.write(f"Статус: {result['status']}\n")
                saved_file.write(f"Комментарии: {result['comments']}\n\n")

        return "\n".join([f"Требование: {res['requirement']}\nСтатус: {res['status']}\nКомментарии: {res['comments']}" for res in results])

    def extract_elements(self, requirement_text):
        elements = {
            "Use Case": re.search(r'Use Case:\s*(.*?)(?=Preconditions:)', requirement_text, re.DOTALL),
            "Actors": re.search(r'Actors:\s*(.*?)(?=Preconditions:)', requirement_text, re.DOTALL),
            "Preconditions": re.search(r'Preconditions:\s*(.*?)(?=Main Scenario:)', requirement_text, re.DOTALL),
            "Main Scenario": re.search(r'Main Scenario:\s*(.*?)(?=Postconditions:)', requirement_text, re.DOTALL),
            "Postconditions": re.search(r'Postconditions:\s*(.*?)(?=Alternative Scenarios:)', requirement_text, re.DOTALL),
            "Alternative Scenarios": re.search(r'Alternative Scenarios:\s*(.*?)(?=Priority:)', requirement_text, re.DOTALL),
            "Priority": re.search(r'Priority:\s*(.*?)(?=Type:)', requirement_text, re.DOTALL),
            "Type": re.search(r'Type:\s*(.*?)(?=\n)', requirement_text, re.DOTALL),
        }
        
        return {k: v.group(1).strip() if v else None for k, v in elements.items()}
