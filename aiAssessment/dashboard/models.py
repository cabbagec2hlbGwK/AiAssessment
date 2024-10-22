from django.db import models

class Report(models.Model):
    email = models.EmailField()
    website_url = models.URLField()
    report_type = models.CharField(max_length=100)
    report_content = models.TextField()

    def __str__(self):
        return f"{self.report_type} report for {self.email}"
