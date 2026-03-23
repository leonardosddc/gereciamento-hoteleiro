from django.urls import path
from .views.hospede import cadastrar_hospede, listar_hospedes, editar_hospede, excluir_hospede

urlpatterns = [
    path('hospedes/', listar_hospedes, name='listar_hospedes'), # R - Read
    path('hospedes/novo/', cadastrar_hospede, name='cadastrar_hospede'), # C - Create
    path('hospedes/editar/<int:id>/', editar_hospede, name='editar_hospede'), # U - Update
    path('hospedes/excluir/<int:id>/', excluir_hospede, name='excluir_hospede'), # D - Delete
]