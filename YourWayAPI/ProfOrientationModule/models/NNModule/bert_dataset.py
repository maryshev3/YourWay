import torch
from torch.utils.data import Dataset

# Dataset class, inherits from torch
class CustomDataset(Dataset):

  def __init__(self, texts, targets, tokenizer, max_len=512):
    """
    Initializes the object with the given texts, targets, tokenizer, and maximum length.

    Parameters:
        texts (list): The list of texts.
        targets (list): The list of targets.
        tokenizer: The tokenizer object.
        max_len (int): The maximum length of the texts.

    Returns:
        None
    """
    self.texts = texts
    self.targets = targets
    self.tokenizer = tokenizer
    self.max_len = max_len

  def __len__(self):
    """
    Returns the length of the object.

    :return: The length of the object.
    :rtype: int
    """
    return len(self.texts)

  def __getitem__(self, idx):
    """
    Get the item from the dataset at the given index.

    Args:
        idx (int): The index of the item to retrieve.

    Returns:
        dict: A dictionary containing the text, input_ids, attention_mask, and targets of the item.
            - 'text' (str): The original text from the dataset.
            - 'input_ids' (torch.Tensor): The input token IDs for the text.
            - 'attention_mask' (torch.Tensor): The attention mask for the input token IDs.
            - 'targets' (torch.Tensor): The target values for the item.
    """
    text = str(self.texts[idx])
    target = self.targets[idx]

    encoding = self.tokenizer.encode_plus(
        text,
        add_special_tokens=True,
        max_length=self.max_len,
        return_token_type_ids=False,
        padding='max_length',
        return_attention_mask=True,
        return_tensors='pt',
        truncation=True
    )

    return {
      'text': text,
      'input_ids': encoding['input_ids'].flatten(),
      'attention_mask': encoding['attention_mask'].flatten(),
      'targets': torch.tensor(target, dtype=torch.long)
    }
