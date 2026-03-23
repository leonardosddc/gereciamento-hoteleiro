import re
from datetime import date
from django import forms
from hotel.models.hospede import Hospede

class HospedeForm(forms.ModelForm):
    class Meta:
        model = Hospede
        fields = ['nome', 'cpf', 'data_nascimento', 'email', 'telefone']
        widgets = {
            'data_nascimento': forms.DateInput(attrs={'type': 'date'}),
        }

    def clean_nome(self):
        nome = self.cleaned_data.get('nome')
        # Exige que tenha pelo menos um espaço (nome e sobrenome)
        if len(nome.strip().split()) < 2:
            raise forms.ValidationError("Por favor, insira seu nome e sobrenome.")
        return nome

    def clean_cpf(self):
        cpf = self.cleaned_data.get('cpf')
        # Remove qualquer coisa que não seja número (pontos, traços, etc)
        cpf_limpo = re.sub(r'[^0-9]', '', cpf)

        # Verifica tamanho e se não é uma sequência igual (ex: 111.111.111-11)
        if len(cpf_limpo) != 11 or cpf_limpo == cpf_limpo[0] * 11:
            raise forms.ValidationError("CPF inválido. Digite 11 números válidos.")

        # Cálculo real para validar o CPF (Matemática do CPF)
        soma = sum(int(cpf_limpo[i]) * (10 - i) for i in range(9))
        digito1 = (soma * 10 % 11) % 10
        if digito1 != int(cpf_limpo[9]):
            raise forms.ValidationError("CPF inválido.")

        soma = sum(int(cpf_limpo[i]) * (11 - i) for i in range(10))
        digito2 = (soma * 10 % 11) % 10
        if digito2 != int(cpf_limpo[10]):
            raise forms.ValidationError("CPF inválido.")

        return cpf_limpo # Salva no banco apenas os números

    def clean_telefone(self):
        telefone = self.cleaned_data.get('telefone')
        # Remove parênteses, espaços e traços
        telefone_limpo = re.sub(r'[^0-9]', '', telefone)
        
        if len(telefone_limpo) < 10 or len(telefone_limpo) > 11:
            raise forms.ValidationError("O telefone deve conter DDD e o número (10 ou 11 dígitos).")
        return telefone_limpo

    def clean_data_nascimento(self):
        data = self.cleaned_data.get('data_nascimento')
        # Verifica se a data escolhida é maior que a data de hoje
        if data and data > date.today():
            raise forms.ValidationError("A data de nascimento não pode estar no futuro.")
        return data