import numpy as np
import torch
from transformers import BertTokenizer, BertForSequenceClassification
from torch.utils.data import Dataset, DataLoader
from transformers import AdamW, get_linear_schedule_with_warmup

from ProfOrientationModule.models.NNModule.bert_dataset import CustomDataset # Используем модифицированную версию класса Dataset из torch.utils.data

class BertClassifier:

    def __init__(self, model_path, tokenizer_path, n_classes=2, epochs=1, max_len=512, model_save_path='/content/bert.pt'):
        """
        Initializes the object with the given model path, tokenizer path, and optional parameters.

        Parameters:
            model_path (str): The path to the model.
            tokenizer_path (str): The path to the tokenizer.
            n_classes (int, optional): The number of classes. Defaults to 2.
            epochs (int, optional): The number of epochs. Defaults to 1.
            max_len (int, optional): The maximum length of the texts. Defaults to 512.
            model_save_path (str, optional): The path to save the model. Defaults to '/content/bert.pt'.

        Returns:
            None
        """
        self.model = BertForSequenceClassification.from_pretrained(model_path)
        self.tokenizer = BertTokenizer.from_pretrained(tokenizer_path)
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model_save_path=model_save_path
        self.max_len = max_len
        self.epochs = epochs
        self.out_features = self.model.bert.encoder.layer[1].output.dense.out_features
        self.model.classifier = torch.nn.Linear(self.out_features, n_classes)
        self.model.to(self.device)
    
    def preparation(self, X_train, y_train, X_valid, y_valid):
        """
        Initializes the necessary datasets and data loaders for training and validation.
        
        Parameters:
            X_train (list): The training data.
            y_train (list): The training labels.
            X_valid (list): The validation data.
            y_valid (list): The validation labels.
        
        Returns:
            None
        """
        # create datasets
        self.train_set = CustomDataset(X_train, y_train, self.tokenizer, max_len=self.max_len)    # Init train set
        self.valid_set = CustomDataset(X_valid, y_valid, self.tokenizer, max_len=self.max_len)    # Init validation set

        # create data loaders
        """
        Data loader. Combines a dataset and a sampler, and provides an iterable over
        the given dataset.
        """
        self.train_loader = DataLoader(self.train_set, batch_size=16, shuffle=True)
        self.valid_loader = DataLoader(self.valid_set, batch_size=16, shuffle=True)

        # helpers initialization
        self.optimizer = AdamW(self.model.parameters(), lr=2e-5, correct_bias=False) # https://arxiv.org/abs/1711.05101#
        self.scheduler = get_linear_schedule_with_warmup(
                self.optimizer,                                             # Uses optimizer
                num_warmup_steps=0,                                         # Warmup steps (Uses for Adam algorithm)
                num_training_steps=len(self.train_loader) * self.epochs     # Count of training steps
            )
        self.loss_fn = torch.nn.CrossEntropyLoss().to(self.device)
            
    def fit(self):
        """
        Fits the model using the training data.

        Returns:
            train_acc (float): The accuracy of the model on the training data.
            train_loss (float): The average loss of the model on the training data.
        """
        self.model = self.model.train()
        losses = []
        correct_predictions = 0

        for data in self.train_loader:
            input_ids = data["input_ids"].to(self.device)
            attention_mask = data["attention_mask"].to(self.device)
            targets = data["targets"].to(self.device)

            outputs = self.model(
                input_ids=input_ids,
                attention_mask=attention_mask
                )

            preds = torch.argmax(outputs.logits, dim=1)
            loss = self.loss_fn(outputs.logits, targets)

            correct_predictions += torch.sum(preds == targets)

            losses.append(loss.item())
            
            loss.backward()
            torch.nn.utils.clip_grad_norm_(self.model.parameters(), max_norm=1.0)
            self.optimizer.step()
            self.scheduler.step()
            self.optimizer.zero_grad()

        train_acc = correct_predictions.double() / len(self.train_set)
        train_loss = np.mean(losses)
        return train_acc, train_loss
    
    def eval(self):
        """
        Evaluates the model on the validation set and returns the accuracy and loss.

        Returns:
            val_acc (float): The accuracy of the model on the validation set.
            val_loss (float): The average loss of the model on the validation set.
        """
        self.model = self.model.eval()
        losses = []
        correct_predictions = 0

        with torch.no_grad():
            for data in self.valid_loader:
                input_ids = data["input_ids"].to(self.device)
                attention_mask = data["attention_mask"].to(self.device)
                targets = data["targets"].to(self.device)

                outputs = self.model(
                    input_ids=input_ids,
                    attention_mask=attention_mask
                    )

                preds = torch.argmax(outputs.logits, dim=1)
                loss = self.loss_fn(outputs.logits, targets)
                correct_predictions += torch.sum(preds == targets)
                losses.append(loss.item())
        
        val_acc = correct_predictions.double() / len(self.valid_set)
        val_loss = np.mean(losses)
        return val_acc, val_loss
    
    def train(self):
        """
        Trains the model for a specified number of epochs.

        Parameters:
            None

        Returns:
            None
        """
        best_accuracy = 0
        for epoch in range(self.epochs):
            print(f'Эпоха {epoch + 1}/{self.epochs}')
            train_acc, train_loss = self.fit()
            print(f'Обучение: потери {train_loss} | точность {train_acc}')

            val_acc, val_loss = self.eval()
            print(f'Валидация: потери {val_loss} | точность {val_acc}')
            print('-' * 10)

            if val_acc > best_accuracy:
                torch.save(self.model, self.model_save_path)
                best_accuracy = val_acc

        self.model = torch.load(self.model_save_path)
    
    def predict(self, text):
        """
        Predicts the class label for a given text.

        Args:
            text (str): The input text to be classified.

        Returns:
            int: The predicted class label.
        """
        encoding = self.tokenizer.encode_plus(
            text,
            add_special_tokens=True,
            max_length=self.max_len,
            return_token_type_ids=False,
            truncation=True,
            padding='max_length',
            return_attention_mask=True,
            return_tensors='pt',
        )
        
        out = {
              'text': text,
              'input_ids': encoding['input_ids'].flatten(),
              'attention_mask': encoding['attention_mask'].flatten()
          }
        
        input_ids = out["input_ids"].to(self.device)
        attention_mask = out["attention_mask"].to(self.device)
        
        outputs = self.model(
            input_ids=input_ids.unsqueeze(0),
            attention_mask=attention_mask.unsqueeze(0)
        )
        
        prediction = torch.argmax(outputs.logits, dim=1).cpu().numpy()[0]

        return prediction

    def load_model(self, model_path):
        """
        Loads the model from a given path.
        
        Args:
            model_path (str): The path to the model.

        Returns:
            None
        """
        self.model = torch.load(model_path, map_location=self.device)