from transformers import DistilBertForSequenceClassification, Trainer, TrainingArguments
from datasets import load_dataset

# Загрузите ваш датасет
dataset = load_dataset("csv", data_files={"train": "path/to/your/train.csv", "validation": "path/to/your/val.csv"})

# Определите модель
model = DistilBertForSequenceClassification.from_pretrained("distilbert-base-uncased", num_labels=2)

# Определите параметры обучения
training_args = TrainingArguments(
    output_dir='./results',
    num_train_epochs=3,
    per_device_train_batch_size=16,
    per_device_eval_batch_size=64,
    warmup_steps=500,
    weight_decay=0.01,
    logging_dir='./logs',
)

# Определите Trainer
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=dataset['train'],
    eval_dataset=dataset['validation']
)

# Запустите обучение
trainer.train()
