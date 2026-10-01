from django.test import TestCase

from . import models


class MachineModelTests(TestCase):
    def test_machine_creation(self):
        models.Machine.objects.create(
            nom="CNC", prix=28_000, duree_de_vie=1, cout_maintenance=1, superficie=1000
        )
        self.assertEqual(models.Machine.objects.count(), 1)


class OperationModelTests(TestCase):
    def test_operation_creation(self):
        machine1 = models.Machine.objects.create(
            nom="CNC", prix=28000, duree_de_vie=1, cout_maintenance=1, superficie=1000
        )
        Produit1 = models.Produit.objects.create(
            nom="Velo",
            prix_de_vente=2800,
            duree_de_vie=10,
            nombre_par_palette=10,
            operations=None,
        )
        Pays1 = models.Pays.objects.create(
            nom="Pays", tva=10, tarif_electrique=1, salaire_minimum=1
        )
        Ville1 = models.Ville.objects.create(
            nom="Ville1", taxe_immobiliere=1, prix_m2=100, pays=Pays1
        )
        QuantiteMachine1 = models.QuantiteMachine.objects.create(
            machine=machine1, nombre=5
        )
        Quantiteproduit1 = models.QuantiteProduit.objects.create(
            produit=Produit1, nombre=28
        )
        Stock1 = models.Stock.objects.create(palettes_max=28)
        Stock1.quantite_produits.add(Quantiteproduit1)
        Stock1.save()
        Lieu1 = models.Lieu.objects.create(
            nom="Lieu1", ville=Ville1, superficie=1000, consomation_electrique=10
        )
        Lieu1.quantite_machine.add(QuantiteMachine1)
        Lieu1.save()

        Produit1 = models.Produit.objects.create(
            nom="Velo",
            prix_de_vente=2800,
            duree_de_vie=10,
            nombre_par_palette=10,
            operations=None,
        )
        OP1 = models.Operation.objects.create(
            nom="OP1",
            operation_suivante=None,
            cout=10,
            machine=machine1,
            heures_de_travail=10,
            consommation_electrique=10,
        )
        OP1.quantite_produits.add(Quantiteproduit1)
        OP1.save()
        self.assertEqual(models.Operation.objects.first().costs(), 30)


class StockModelTests(TestCase):
    def test_stock_creation(self):
        Produit1 = models.Produit.objects.create(
            nom="Velo",
            prix_de_vente=2800,
            duree_de_vie=10,
            nombre_par_palette=10,
            operations=None,
        )
        Quantiteproduit1 = models.QuantiteProduit.objects.create(
            produit=Produit1, nombre=28
        )
        Stock1 = models.Stock.objects.create(palettes_max=28)
        Stock1.quantite_produits.add(Quantiteproduit1)
        Stock1.save()
