class Translator:
  def __init__(self, lang, translations):
    self.lang = lang
    self.translations = translations
    self.bindings = []

  def bind(self, widget, attr, key):
    self.bindings.append((widget, attr, key))
    setattr(widget, attr, self.t(key))

  def t(self, key):
    return self.translations.get(self.lang, {}).get(key, key)
  
  def t_fmt(self, key, **kwargs):
    template = self.t(key)
    return template.format(**kwargs)
  
  def set_lang(self, lang):
    self.lang = lang
    for widget, attr, key in self.bindings:
      setattr(widget,attr, self.t(key))
      widget.update()