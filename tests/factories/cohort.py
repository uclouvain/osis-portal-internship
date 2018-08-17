import factory.fuzzy
import datetime


class CohortFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = 'internship.Cohort'

    name = factory.Sequence(lambda n: 'Cohort %d' % (n,))
    description = factory.fuzzy.FuzzyText()

    free_internships_number = 8
    publication_start_date = datetime.datetime.today().replace(day=1)
    subscription_start_date = datetime.datetime.today().replace(day=1).replace(month=datetime.datetime.today().month - 1)
    subscription_end_date = datetime.datetime.today().replace(day=1).replace(month=datetime.datetime.today().month + 2)
