class UnicodeSlugConverter:
    """
    日本語を含むスラッグ(slugify(..., allow_unicode=True)で生成されたもの)を
    URLパターンで受け付けるためのコンバーター。
    Django標準の`slug`コンバーターは半角英数字のみしか許可しないため、
    日本語の商品名から生成されたスラッグを解決できない問題への対応。
    """
    regex = r'[-\w]+'

    def to_python(self, value):
        return value

    def to_url(self, value):
        return value
