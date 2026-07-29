from django import forms
from django.core.exceptions import ValidationError

class UploadExcelForm(forms.Form):
    arquivo_excel = forms.FileField(
        label='Selecione o arquivo Excel',
        help_text='Apenas arquivos .xlsx são permitidos.'
    )

    def clean_arquivo_excel(self):
        arquivo = self.cleaned_data.get('arquivo_excel')
        if arquivo:
            if not arquivo.name.endswith('.xlsx'):
                raise ValidationError('O arquivo precisa ter a extensão .xlsx')
        return arquivo
