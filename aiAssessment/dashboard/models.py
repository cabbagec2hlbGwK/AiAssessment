from django.db import models

# class Report(models.Model):
#     email = models.EmailField()
#     website_url = models.URLField()
#     report_type = models.CharField(max_length=100)
#     report_content = models.TextField()

#     def __str__(self):
#         return f"{self.report_type} report for {self.email}"


# class UserReg(models.Model):
#     USER_JOB_STATE_CHOICES = [
#         ('success', 'Success'),
#         ('error', 'Error'),
#         ('expired', 'Expired'),
#         ('active', 'Active'),
#         ('waiting', 'Waiting')
#     ]

#     userId = models.CharField(max_length=255, primary_key=True)
#     name = models.CharField(max_length=255)
#     email = models.EmailField(max_length=255)
#     endpoint = models.CharField(max_length=255)
#     Detailed = models.BooleanField(default=False)
#     jobState = models.CharField(max_length=7, choices=USER_JOB_STATE_CHOICES, default='waiting')
#     timeStamp = models.DateTimeField(auto_now_add=True)
#     counter = models.IntegerField(default=0)
#     resultData = models.BinaryField(null=True, blank=True) 
#     information = models.CharField(max_length=255, default='')

#     def __str__(self):
#         return self.userId
