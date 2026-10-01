from django.db import models


class Operation(models.Model):
    nom = models.CharField(max_length=100)
    operation_suivante = models.ForeignKey(
        "self", blank=True, null=True, on_delete=models.PROTECT
    )
    cout = models.IntegerField()
    machine = models.ForeignKey("Machine", on_delete=models.PROTECT)
    quantite_produits = models.ManyToManyField("QuantiteProduit")
    heures_de_travail = models.IntegerField()
    consommation_electrique = models.IntegerField()

    def __str__(self):
        return self.nom

    def costs(self):
        return (
            self.cout
            + self.heures_de_travail
            * self.machine.quantitemachine_set.first()
            .lieu_set.first()
            .ville.pays.salaire_minimum
            + self.consommation_electrique
            * self.machine.quantitemachine_set.first()
            .lieu_set.first()
            .ville.pays.tarif_electrique
        )


class Produit(models.Model):
    nom = models.CharField(max_length=100)
    prix_de_vente = models.IntegerField()
    duree_de_vie = models.IntegerField()
    nombre_par_palette = models.IntegerField()
    operations = models.ForeignKey(
        Operation, blank=True, null=True, on_delete=models.PROTECT
    )

    def __str__(self):
        return self.nom

    def costs(self):
        s = 0
        operation = self.operations
        while operation.operation_suivante:
            s = s + operation.costs
            operation = operation.operation_suivante

        return s


class QuantiteProduit(models.Model):
    produit = models.ForeignKey(Produit, on_delete=models.PROTECT)
    nombre = models.IntegerField()

    def costs(self):
        return self.produit.costs() * self.nombre


class Stock(models.Model):
    quantite_produits = models.ManyToManyField(QuantiteProduit)
    palettes_max = models.IntegerField()

    def costs(self):
        return self.cout


class PointDeVente(models.Model):
    nom = models.CharField(max_length=100)
    lieu = models.ForeignKey("Lieu", on_delete=models.PROTECT)
    heures_de_travail = models.IntegerField()
    stock = models.ForeignKey(Stock, on_delete=models.PROTECT)

    def __str__(self):
        return self.nom


class Facture(models.Model):
    quantite_produits = models.ManyToManyField(QuantiteProduit)
    reduction = models.IntegerField()
    point_de_vente = models.ForeignKey(PointDeVente, on_delete=models.PROTECT)
    client = models.CharField(max_length=100)

    def __str__(self):
        return self.client


class Pays(models.Model):
    nom = models.CharField(max_length=100)
    tva = models.IntegerField()
    tarif_electrique = models.IntegerField()
    salaire_minimum = models.IntegerField()

    def __str__(self):
        return self.nom


class Ville(models.Model):
    nom = models.CharField(max_length=100)
    taxe_immobiliere = models.IntegerField()
    prix_m2 = models.IntegerField()
    pays = models.ForeignKey(Pays, on_delete=models.PROTECT)

    def __str__(self):
        return self.nom


class Machine(models.Model):
    nom = models.CharField(max_length=100)
    prix = models.IntegerField()
    duree_de_vie = models.IntegerField()
    cout_maintenance = models.IntegerField()
    superficie = models.IntegerField()

    def __str__(self):
        return self.nom

    def costs(self):
        return self.prix


class QuantiteMachine(models.Model):
    machine = models.ForeignKey(Machine, on_delete=models.PROTECT)
    nombre = models.IntegerField()


class Lieu(models.Model):
    nom = models.CharField(max_length=100)
    ville = models.ForeignKey(Ville, on_delete=models.PROTECT)
    superficie = models.IntegerField()
    quantite_machine = models.ManyToManyField(QuantiteMachine, blank=True, null=True)
    consomation_electrique = models.IntegerField()

    def __str__(self):
        return self.nom

    def costs(self):
        return (
            self.ville.prix_m2 * self.superficie
            + self.consomation_electrique * self.ville.pays.tarif_electrique
        )


class Transport(models.Model):
    nom = models.CharField(max_length=100, default="transport")
    nombre_palettes = models.IntegerField()
    cout = models.IntegerField()
    delai = models.IntegerField()
    depart = models.ForeignKey(Lieu, on_delete=models.PROTECT, related_name="depart+")
    arrivee = models.ForeignKey(Lieu, on_delete=models.PROTECT)

    def __str__(self):
        return self.nom

    def costs(self):
        return self.cout


class PrixProduit(models.Model):
    produit = models.ForeignKey(Produit, on_delete=models.PROTECT)
    prix_achat = models.IntegerField()


class Fournisseur(models.Model):
    nom = models.CharField(max_length=100)
    prix_produits = models.ManyToManyField(PrixProduit)

    def __str__(self):
        return self.nom
