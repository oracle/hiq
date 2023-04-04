"""
+🔵
├── +embeddings (BertEmbeddings)
│   ├── +word_embeddings (Embedding) weight:[30522, 768]
│   ├── +position_embeddings (Embedding) weight:[512, 768]
│   ├── +token_type_embeddings (Embedding) weight:[2, 768]
│   └── +LayerNorm (LayerNorm) weight:[768] bias:[768]
├── +encoder (BertEncoder)
│   └── +layer (ModuleList)
│       └── 0-11(BertLayer)
│           ├── +attention (BertAttention)
│           │   ├── +self (BertSelfAttention)
│           │   │   └── query,key,value(Linear) weight:[768, 768] bias:[768]
│           │   └── +output (BertSelfOutput)
│           │       ├── +dense (Linear) weight:[768, 768] bias:[768]
│           │       └── +LayerNorm (LayerNorm) weight:[768] bias:[768]
│           ├── +intermediate (BertIntermediate)
│           │   └── +dense (Linear) weight:[3072, 768] bias:[3072]
│           └── +output (BertOutput)
│               ├── +dense (Linear) weight:[768, 3072] bias:[768]
│               └── +LayerNorm (LayerNorm) weight:[768] bias:[768]
└── +pooler (BertPooler)
    └── +dense (Linear) weight:[768, 768] bias:[768]
"""

from transformers import BertModel
from hiq.vis import print_model

model = BertModel.from_pretrained("bert-base-uncased")

print("*" * 80)
print_model(model)
