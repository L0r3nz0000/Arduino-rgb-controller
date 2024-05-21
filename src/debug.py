class Info:
  def __init__(self):
    self.debug_mode = False
  def __init__(self, debug):
    self.debug_mode = debug

  def DEBUG(self, text: str):
    if self.debug_mode:
      print("\u001b[36mDEBUG: \u001b[0m" + text)

  def SUCCESS(text: str):
    print("\u001b[32m" + text + "\u001b[0m")
  
  def ERROR(text: str, _exit: bool = False):
    print("\u001b[31mERROR: \u001b[0m" + text)
    if _exit:
      exit()