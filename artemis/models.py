from django.conf import settings
from django.db import models


class Treatment(models.Model):

    label = models.IntegerField()
    description = models.CharField(max_length=128)


class Site(models.Model):

    name = models.CharField(max_length=128)

    def __unicode__(self):
        return u'%s' % self.name

    def __str__(self):
        return self.name


class Plot(models.Model):

    site = models.ForeignKey(Site, on_delete=models.CASCADE)
    label = models.IntegerField()
    treatment = models.ForeignKey(Treatment, on_delete=models.CASCADE)

    pH_mean = models.FloatField(blank=True, null=True)
    pH_sd = models.FloatField(blank=True, null=True)

    pHCa_mean = models.FloatField(blank=True, null=True)
    pHCa_sd = models.FloatField(blank=True, null=True)

    EC_mean = models.FloatField(blank=True, null=True)
    EC_sd = models.FloatField(blank=True, null=True)


class Replicate(models.Model):

    plot = models.ForeignKey(Plot, on_delete=models.CASCADE)
    label = models.IntegerField()

    pH = models.FloatField(blank=True, null=True)
    pHCa = models.FloatField(blank=True, null=True)
    EC = models.FloatField(blank=True, null=True)


class Coordinate(models.Model):

    # coordinates can be associated with a Site or a Plot
    site = models.ForeignKey(Site, on_delete=models.CASCADE, blank=True, null=True)
    replicate = models.ForeignKey(Replicate, on_delete=models.CASCADE, blank=True, null=True)
    
    # north, east, center, etc.
    label = models.CharField(max_length=31, blank=True, null=True)
    
    latitude = models.FloatField()
    longitude = models.FloatField()


class Mineralogy(models.Model):

    site = models.ForeignKey(Site, on_delete=models.CASCADE)
    replicate = models.ForeignKey(Replicate, on_delete=models.CASCADE, blank=True, null=True)
    collection_date = models.DateField(blank=True, null=True)
    time_label = models.IntegerField()

    min_depth = models.IntegerField()
    max_depth = models.IntegerField()
    
    quartz = models.FloatField(blank=True, null=True)
    plagioclase = models.FloatField(blank=True, null=True)
    illite = models.FloatField(blank=True, null=True)
    chlorite = models.FloatField(blank=True, null=True)
    kaolinite = models.FloatField(blank=True, null=True)
    pyrite = models.FloatField(blank=True, null=True)
    gypsum = models.FloatField(blank=True, null=True)
    jarosite = models.FloatField(blank=True, null=True)
    melanternite = models.FloatField(blank=True, null=True)
    ankerite = models.FloatField(blank=True, null=True)
    siderite = models.FloatField(blank=True, null=True)
    amorphous = models.FloatField(blank=True, null=True)
  
class Geochemistry(models.Model):

    # Geochemistry can be associated with a Site OR Replicate
    site = models.ForeignKey(Site, on_delete=models.CASCADE)
    replicate = models.ForeignKey(Replicate, on_delete=models.CASCADE, blank=True, null=True)
    collection_date = models.DateField(blank=True, null=True)
    time_label = models.IntegerField()

    min_depth = models.IntegerField()
    max_depth = models.IntegerField()

    pH = models.FloatField(blank=True, null=True)
    EC = models.FloatField(blank=True, null=True)
    color = models.CharField(max_length=15, blank=True, null=True)

    Ag = models.FloatField(blank=True, null=True)
    Al = models.FloatField(blank=True, null=True)
    As = models.FloatField(blank=True, null=True)
    Au = models.FloatField(blank=True, null=True)
    Ba = models.FloatField(blank=True, null=True)
    Be = models.FloatField(blank=True, null=True)
    Bi = models.FloatField(blank=True, null=True)
    Br = models.FloatField(blank=True, null=True)
    Ca = models.FloatField(blank=True, null=True)
    Cd = models.FloatField(blank=True, null=True)
    Ce = models.FloatField(blank=True, null=True)
    Co = models.FloatField(blank=True, null=True)
    Cr = models.FloatField(blank=True, null=True)
    Cs = models.FloatField(blank=True, null=True)
    Cu = models.FloatField(blank=True, null=True)
    Dy = models.FloatField(blank=True, null=True)
    Er = models.FloatField(blank=True, null=True)
    Eu = models.FloatField(blank=True, null=True)
    Fe = models.FloatField(blank=True, null=True)
    Ga = models.FloatField(blank=True, null=True)
    Gd = models.FloatField(blank=True, null=True)
    Ge = models.FloatField(blank=True, null=True)
    Hf = models.FloatField(blank=True, null=True)
    Ho = models.FloatField(blank=True, null=True)
    In = models.FloatField(blank=True, null=True)
    Ir = models.FloatField(blank=True, null=True)
    K = models.FloatField(blank=True, null=True)
    La = models.FloatField(blank=True, null=True)
    Lu = models.FloatField(blank=True, null=True)
    Mg = models.FloatField(blank=True, null=True)
    Mn = models.FloatField(blank=True, null=True)
    Mo = models.FloatField(blank=True, null=True)
    Na = models.FloatField(blank=True, null=True)
    Nb = models.FloatField(blank=True, null=True)
    Nd = models.FloatField(blank=True, null=True)
    Ni = models.FloatField(blank=True, null=True)
    P = models.FloatField(blank=True, null=True)
    Pb = models.FloatField(blank=True, null=True)
    Pr = models.FloatField(blank=True, null=True)
    Rb = models.FloatField(blank=True, null=True)
    S = models.FloatField(blank=True, null=True)
    Sb = models.FloatField(blank=True, null=True)
    Sc = models.FloatField(blank=True, null=True)
    Se = models.FloatField(blank=True, null=True)
    Si = models.FloatField(blank=True, null=True)
    Sm = models.FloatField(blank=True, null=True)
    Sn = models.FloatField(blank=True, null=True)
    Sr = models.FloatField(blank=True, null=True)
    Ta = models.FloatField(blank=True, null=True)
    Tb = models.FloatField(blank=True, null=True)
    Th = models.FloatField(blank=True, null=True)
    Ti = models.FloatField(blank=True, null=True)
    Tl = models.FloatField(blank=True, null=True)
    Tm = models.FloatField(blank=True, null=True)
    U = models.FloatField(blank=True, null=True)
    V = models.FloatField(blank=True, null=True)
    W = models.FloatField(blank=True, null=True)
    Y = models.FloatField(blank=True, null=True)
    Yb = models.FloatField(blank=True, null=True)
    Zn = models.FloatField(blank=True, null=True)
    Zr = models.FloatField(blank=True, null=True)


class Extraction(models.Model):

    site = models.ForeignKey(Site, on_delete=models.CASCADE)
    collection_date = models.DateField(blank=True, null=True)
    time_label = models.IntegerField()
    element = models.CharField(max_length=15)

    min_depth = models.IntegerField()
    max_depth = models.IntegerField()

    H20 = models.FloatField(blank=True, null=True)
    H20_sd = models.FloatField(blank=True, null=True)
    AmNO3 = models.FloatField(blank=True, null=True)
    AmNO3_sd = models.FloatField(blank=True, null=True)
    AAc = models.FloatField(blank=True, null=True)
    AAc_sd = models.FloatField(blank=True, null=True)
    PO4 = models.FloatField(blank=True, null=True)
    PO4_sd = models.FloatField(blank=True, null=True)
    AAO = models.FloatField(blank=True, null=True)
    AAO_sd = models.FloatField(blank=True, null=True)
    CDB = models.FloatField(blank=True, null=True)
    CDB_sd = models.FloatField(blank=True, null=True)