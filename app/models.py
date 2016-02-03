from django.db import models

#DATABASE VIEWS
class Elements(models.Model):
    element_id = models.CharField(primary_key=True, max_length=255)
    label = models.CharField(max_length=128, blank=True, null=True)
    
    class Meta:
        managed = False
        db_table = 'elements'
    def __str__(self):
        return self.label