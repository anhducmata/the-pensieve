import csv

class DataHandler:
  def __init__(self, storage_location):
    self.storage_location = storage_location

  def save_entry(self, entry):
    """
    Saves a new entry as a new row in the CSV file.

    Args:
        entry (str): The diary entry to be saved.
    """
    with open(self.storage_location, "a", newline="") as csvfile:
      writer = csv.writer(csvfile)
      writer.writerow([entry])  # Write entry as a single-element list

  def load_entries(self):
    """
    Loads all entries from the CSV file and returns them as a list.

    Returns:
        list: A list of strings containing all diary entries.
    """
    entries = []
    with open(self.storage_location, "r") as csvfile:
      reader = csv.reader(csvfile)
      for row in reader:
        entries.append(row[0])  # Assuming each row has a single entry (column)
    return entries

  def close(self):
    pass  # No specific closing required for CSV files
