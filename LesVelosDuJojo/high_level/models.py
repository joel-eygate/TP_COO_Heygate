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

    def json(self):
        return {
            "nom": self.nom,
            "operation suivante": self.operation_suivante,
            "cout": self.cout,
            "machine": self.machine,
            "quantite produit": [v.pk for v in self.quantite_produits],
            "Heures de travail": self.heures_de_travail,
            "consommation_electrique": self.consommation_electrique,
        }


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

    def json(self):
        return {
            "nom": self.nom,
            "prix_de_vente": self.prix_de_vente,
            "duree_de_vie": self.duree_de_vie,
            "nombre_par_palette": self.nombre_par_palette,
            "operation": self.operations,
        }


class QuantiteProduit(models.Model):
    produit = models.ForeignKey(Produit, on_delete=models.PROTECT)
    nombre = models.IntegerField()

    def costs(self):
        return self.produit.costs() * self.nombre

    def json(self):
        return {"produit": self.produit, "nombre": self.nombre}


class Stock(models.Model):
    quantite_produits = models.ManyToManyField(QuantiteProduit)
    palettes_max = models.IntegerField()

    def costs(self):
        return self.cout

    def json(self):
        return {
            "quantite produit": [v.pk for v in self.quantite_produits],
            "palettes_max": self.palettes_max,
        }


class PointDeVente(models.Model):
    nom = models.CharField(max_length=100)
    lieu = models.ForeignKey("Lieu", on_delete=models.PROTECT)
    heures_de_travail = models.IntegerField()
    stock = models.ForeignKey(Stock, on_delete=models.PROTECT)

    def __str__(self):
        return self.nom

    def json(self):
        return {
            "nom": self.nom,
            "lieu": self.lieu,
            "heures_de_travail": self.heures_de_travail,
            "stock": self.stock,
        }


class Facture(models.Model):
    quantite_produits = models.ManyToManyField(QuantiteProduit)
    reduction = models.IntegerField()
    point_de_vente = models.ForeignKey(PointDeVente, on_delete=models.PROTECT)
    client = models.CharField(max_length=100)

    def __str__(self):
        return self.client

    def json(self):
        return {
            "quantite produit": [v.pk for v in self.quantite_produits],
            "reduction": self.reduction,
            "point_de_vente": self.point_de_vente,
            "client": self.client,
        }


class Pays(models.Model):
    nom = models.CharField(max_length=100)
    tva = models.IntegerField()
    tarif_electrique = models.IntegerField()
    salaire_minimum = models.IntegerField()

    def __str__(self):
        return self.nom

    def json(self):
        return {
            "nom": self.nom,
            "tva": self.tva,
            "tarif_electrique": self.tarif_electrique,
            "salaire_minimum": self.salaire_minimum,
        }


class Ville(models.Model):
    nom = models.CharField(max_length=100)
    taxe_immobiliere = models.IntegerField()
    prix_m2 = models.IntegerField()
    pays = models.ForeignKey(Pays, on_delete=models.PROTECT)

    def __str__(self):
        return self.nom

    def json(self):
        return {
            "nom": self.nom,
            "taxe_immobiliere": self.taxe_immobiliere,
            "prix_m2": self.prix_m2,
            "pays": self.pays,
        }


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

    def json(self):
        return {
            "nom": self.nom,
            "prix": self.prix,
            "duree_de_vie": self.duree_de_vie,
            "cout_maintenance": self.cout_maintenance,
            "superficie": self.superficie,
        }


class QuantiteMachine(models.Model):
    machine = models.ForeignKey(Machine, on_delete=models.PROTECT)
    nombre = models.IntegerField()

    def json(self):
        return {"machine": self.machine, "nombre": self.nombre}


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

    def json(self):
        return {
            "nom": self.nom,
            "ville": self.ville,
            "superficie": self.superficie,
            "quantite_machine": [v.pk for v in self.quantite_machine],
            "consomation_electrique": self.consomation_electrique,
        }


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

    def json(self):
        return {
            "nom": self.nom,
            "nombre_palettes": self.nombre_palettes,
            "cout": self.cout,
            "delai": self.delai,
            "depart": self.depart,
            "arrivee": self.arrivee,
        }


class PrixProduit(models.Model):
    produit = models.ForeignKey(Produit, on_delete=models.PROTECT)
    prix_achat = models.IntegerField()

    def json(self):
        return {"produit": self.produit, "prix_achat": self.prix_achat}


class Fournisseur(models.Model):
    nom = models.CharField(max_length=100)
    prix_produits = models.ManyToManyField(PrixProduit)

    def __str__(self):
        return self.nom

    def json(self):
        return {"nom": self.nom, "prix_produits": [v.pk for v in self.prix_produits]}
