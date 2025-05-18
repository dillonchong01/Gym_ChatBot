import pandas as pd
from transformers import AutoTokenizer, AutoModelForSequenceClassification, Trainer, TrainingArguments, EarlyStoppingCallback
from sklearn.model_selection import train_test_split
from datasets import Dataset
from sklearn.metrics import accuracy_score, f1_score
from onnxruntime.quantization import quantize_dynamic, QuantType

# Import Data
df = pd.read_csv("intent_model/model_training/Intent_Train_Data.csv")
texts = df["Text"].tolist()
labels = df["Label"].tolist()

# Split Data into Train/Test
train_texts, test_texts, train_labels, test_labels = train_test_split(texts, labels, test_size=0.2, random_state=42)

# Tokenize and Save Tokenizer
tokenizer = AutoTokenizer.from_pretrained("huawei-noah/TinyBERT_General_4L_312D")
train_encodings = tokenizer(list(train_texts), truncation=True, padding=True)
test_encodings = tokenizer(list(test_texts), truncation=True, padding=True)
tokenizer.save_pretrained("./intent_model")

# Create HuggingFace Dataset
train_dataset = Dataset.from_dict({
    'input_ids': train_encodings['input_ids'],
    'attention_mask': train_encodings['attention_mask'],
    'labels': train_labels
})
val_dataset = Dataset.from_dict({
    'input_ids': test_encodings['input_ids'],
    'attention_mask': test_encodings['attention_mask'],
    'labels': test_labels
})

# Load Pretrained Model
model = AutoModelForSequenceClassification.from_pretrained("huawei-noah/TinyBERT_General_4L_312D", num_labels=4)

# Specify Training Parameters
training_args = TrainingArguments(
    output_dir="./results",
    evaluation_strategy="epoch",        # Evaluate by Epoch
    save_strategy="epoch",
    metric_for_best_model="eval_accuracy",
    load_best_model_at_end=True,
    learning_rate=2e-5,
    per_device_train_batch_size=4,
    per_device_eval_batch_size=4,
    num_train_epochs=20,
    weight_decay=0.01,
    logging_dir=None,
    logging_steps=10
)

# Evaliuation Metrics
def compute_metrics(pred):
    labels = pred.label_ids
    preds = pred.predictions.argmax(-1)
    acc = accuracy_score(labels, preds)
    f1 = f1_score(labels, preds, average='weighted')
    return {
        'accuracy': acc,
        'f1': f1,
    }

# Train the Model
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
    eval_dataset=val_dataset,
    compute_metrics=compute_metrics,
    callbacks=[EarlyStoppingCallback(early_stopping_patience=4)]
)
trainer.train()

# Save the Model
from transformers.onnx import export
from transformers.onnx.features import FeaturesManager
from pathlib import Path
_, model_onnx_config = FeaturesManager.check_supported_model_or_raise(model, feature="sequence-classification")
onnx_config = model_onnx_config(model.config)

# Save Base Model
export(
    preprocessor=tokenizer,
    model=model,
    config=onnx_config,
    opset=11,
    output=Path("./intent_model/intent_model.onnx")
)

# Quantize and Save Model
quantize_dynamic(
    model_input="intent_model/intent_model.onnx",
    model_output="intent_model/intent_model_quantized.onnx",
    weight_type=QuantType.QInt8
)