import torch
from torch.utils.data import TensorDataset, DataLoader, RandomSampler
from transformers import BertTokenizer, BertForSequenceClassification

# Detectar si GPU Intel está disponible
if torch.xpu.is_available():
    device = torch.device("xpu")
    print("GPU Intel detectada y disponible para uso.")
else:
    device = torch.device("cpu")
    print("GPU Intel no detectada. Usando CPU.")

# Definir clases
labels = {"EJECUTAR_COMANDO": 0, "EJECUTAR_ASISTENTE": 1, "APRENDER": 2}

# Datos de ejemplo
texts = [
    "Apaga la luz",
    "¿Puedes ayudarme con esto?",
    "Quiero saber cómo funciona el aprendizaje profundo.",
    "Inicia la música",
    "Explícame el funcionamiento del modelo BERT",
    "Llama a mi asistente"
]
labels_list = [0, 1, 2, 0, 2, 1]

# Cargar tokenizador
tokenizer = BertTokenizer.from_pretrained("bert-base-uncased")

# Tokenizar todos los textos
encodings = tokenizer(texts, padding=True, truncation=True, max_length=32, return_tensors="pt")

# Convertir etiquetas en tensor
labels_tensor = torch.tensor(labels_list)

# Crear dataset con input_ids, attention_mask y etiquetas
dataset = TensorDataset(encodings['input_ids'], encodings['attention_mask'], labels_tensor)

# Crear DataLoader con sampler aleatorio y batch size 2
batch_size = 2
dataloader = DataLoader(dataset, sampler=RandomSampler(dataset), batch_size=batch_size)

# Cargar modelo BERT para clasificación con 3 clases
model = BertForSequenceClassification.from_pretrained("bert-base-uncased", num_labels=3)
model.to(device)

# Ejemplo de iterar sobre los batches del DataLoader y hacer forward pass
model.train()  # modo entrenamiento
for batch in dataloader:
    input_ids, attention_mask, labels = [x.to(device) for x in batch]
    outputs = model(input_ids=input_ids, attention_mask=attention_mask, labels=labels)
    loss = outputs.loss
    logits = outputs.logits
    print("Batch loss:", loss.item())
    print("Predicciones:", torch.argmax(logits, dim=1))
