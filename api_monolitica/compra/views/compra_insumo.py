from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.db import transaction, models

from ..serializers.compra_insumo import CompraInsumoSerializer
from ..models.compra_insumo import CompraInsumo
from ..models.compra import Compra
from insumo.models import Insumo

class CompraInsumoViewSet(viewsets.ModelViewSet):
    queryset = CompraInsumo.objects.all()
    serializer_class = CompraInsumoSerializer

    def get_queryset(self):
        compra_id = self.request.query_params.get('compra_id')
        if compra_id:
            return CompraInsumo.objects.filter(compra_id=compra_id)
        return CompraInsumo.objects.all()

    @action(detail=False, methods=['post'], url_path='batch')
    def create_batch(self, request):
        data = request.data
        if not isinstance(data, list):
            return Response({"error": "Se esperaba una lista de objetos"}, status=status.HTTP_400_BAD_REQUEST)

        created_items = []
        errors = []
        compras_afectadas = set()

        with transaction.atomic():
            for entry in data:
                try:
                    # Calcular subtotal si no viene incluido
                    if 'cantidad' in entry and 'precioUnitario' in entry and 'subtotal' not in entry:
                        entry['subtotal'] = entry['cantidad'] * entry['precioUnitario']

                    compra_insumo_instance = None
                    if 'id' in entry:
                        try:
                            compra_insumo_instance = CompraInsumo.objects.get(id=entry['id'])
                        except CompraInsumo.DoesNotExist:
                            errors.append({"error": f"El CompraInsumo con ID {entry['id']} no existe"})
                            transaction.set_rollback(True)
                            break

                    serializer = self.get_serializer(instance=compra_insumo_instance, data=entry)
                    if serializer.is_valid():
                        compra_insumo = serializer.save()
                        compras_afectadas.add(compra_insumo.compra_id.id)
                        created_items.append(serializer.data)
                    else:
                        errors.append(serializer.errors)
                        transaction.set_rollback(True)
                        break

                except Insumo.DoesNotExist:
                    errors.append({"error": f"El insumo con ID {entry.get('insumo_id')} no existe"})
                    transaction.set_rollback(True)
                    break
                except Compra.DoesNotExist:
                    errors.append({"error": f"La compra con ID {entry.get('compra_id')} no existe"})
                    transaction.set_rollback(True)
                    break
                except Exception as e:
                    errors.append({"error": str(e)})
                    transaction.set_rollback(True)
                    break

            # Recalcular totales UNA SOLA VEZ por compra afectada
            if not errors:
                for compra_id in compras_afectadas:
                    try:
                        compra = Compra.objects.get(id=compra_id)
                        total_subtotales = CompraInsumo.objects.filter(compra_id=compra).aggregate(
                            total=models.Sum('subtotal')
                        )['total'] or 0

                        total_con_iva = total_subtotales + (total_subtotales * compra.IVA)
                        compra.total = total_con_iva
                        compra.save()
                    except Compra.DoesNotExist:
                        # Esto no debería pasar, pero lo capturamos igual
                        errors.append({"error": f"La compra con ID {compra_id} no existe para recalcular total"})
                        transaction.set_rollback(True)
                        break

        if errors:
            return Response({"created": created_items, "errors": errors}, status=status.HTTP_207_MULTI_STATUS)
        return Response({"created": created_items}, status=status.HTTP_201_CREATED)
