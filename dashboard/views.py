import json
import os
from random import randint

import numpy as np
import pandas as pd
from django.db.models import Sum, Avg
from django.shortcuts import render
from .models import *
from .utilities import reorder, PreProcessing
import pickle as pkl


# Create your views here.
def fb_dashboard(request):
    fb_stats = SocialMediaDataset.objects.filter(Account='Facebook')
    counts = fb_stats.values('Month').order_by('Month').annotate(sum=Sum('Totalengagement2'))
    counts_format = fb_stats.values('Format').order_by('Format').annotate(sum=Sum('Totalengagement2'))
    dates, dataset = reorder(qs=counts)
    labels, datasets, PostFormats = reorder(qs=counts_format, chart=2)
    top_posts = fb_stats.values('Date', 'Post', 'Impressions', 'Totalengagement2').order_by('-Totalengagement2')[:5]

    context = {
        'impressions': f"{fb_stats.aggregate(Sum('Impressions'))['Impressions__sum']:,}",
        'engagements': round(fb_stats.aggregate(Avg('Totalengagement'))['Totalengagement__avg'], 2),
        'ctr': round(fb_stats.aggregate(Avg('ClickThroughrate'))['ClickThroughrate__avg'], 2),
        'likes_folows': fb_stats.aggregate(Sum('Likes'))['Likes__sum'] + fb_stats.aggregate(Sum('Follows'))[
            'Follows__sum'],
        'dates': dates,
        'dataset': dataset,
        'labels': labels,
        'datasets': datasets,
        'PostFormats': PostFormats, 'top_posts': top_posts
    }
    return render(request, 'dashboard/fb.html', context)


def tw_dashboard(request):
    tw_stats = SocialMediaDataset.objects.filter(Account='Twitter')
    counts = tw_stats.values('Month').order_by('Month').annotate(sum=Sum('Totalengagement2'))
    dates, dataset = reorder(qs=counts)
    counts_format = tw_stats.values('Format').order_by('Format').annotate(sum=Sum('Totalengagement2'))
    labels, datasets, PostFormats = reorder(qs=counts_format, chart=2)
    top_posts = tw_stats.values('Date', 'Post', 'Impressions', 'Totalengagement2').order_by('-Totalengagement2')[:5]
    context = {
        'impressions': f"{tw_stats.aggregate(Sum('Impressions'))['Impressions__sum']:,}",
        'engagements': round(tw_stats.aggregate(Avg('Totalengagement'))['Totalengagement__avg'], 2),
        'ctr': round(tw_stats.aggregate(Avg('ClickThroughrate'))['ClickThroughrate__avg'], 2),
        'likes_folows': f"{tw_stats.aggregate(Sum('Likes'))['Likes__sum'] + tw_stats.aggregate(Sum('Follows'))['Follows__sum']:,}",
        'dates': dates,
        'dataset': dataset, 'labels': labels, 'datasets': datasets,
        'PostFormats': PostFormats, 'top_posts': top_posts

    }
    return render(request, 'dashboard/tw.html', context)


def lk_dashboard(request):
    lk_stats = SocialMediaDataset.objects.filter(Account='LinkedIn')
    counts = lk_stats.values('Month').order_by('Month').annotate(sum=Sum('Totalengagement2'))
    dates, dataset = reorder(qs=counts)
    counts_format = lk_stats.values('Format').order_by('Format').annotate(sum=Sum('Totalengagement2'))
    labels, datasets, PostFormats = reorder(qs=counts_format, chart=2)
    top_posts = lk_stats.values('Date', 'Post', 'Impressions', 'Totalengagement2').order_by('-Totalengagement2')[:5]
    context = {
        'impressions': f"{lk_stats.aggregate(Sum('Impressions'))['Impressions__sum']:,}",
        'engagements': round(lk_stats.aggregate(Avg('Totalengagement'))['Totalengagement__avg'], 2),
        'ctr': round(lk_stats.aggregate(Avg('ClickThroughrate'))['ClickThroughrate__avg'], 2),
        'likes_folows': f"{lk_stats.aggregate(Sum('Likes'))['Likes__sum'] + lk_stats.aggregate(Sum('Follows'))['Follows__sum']:,}",
        'dates': dates,
        'dataset': dataset, 'labels': labels, 'datasets': datasets,
        'PostFormats': PostFormats, 'top_posts': top_posts

    }
    return render(request, 'dashboard/lk.html', context)


def nba(request):
    df = pd.DataFrame(list(SocialMediaDataset.objects.values())).sample(500)
    df.Date = pd.to_datetime('now')

    preproc = PreProcessing()
    model_object = os.path.abspath("xgbmodel.pk")
    with open(model_object, 'rb') as f:
        loaded_model = pkl.load(f)
    scaler = loaded_model[0]
    xgmodel = loaded_model[1]
    # # return model results
    transformed_test = preproc.transform(df)
    scale_numeric = scaler.transform(transformed_test[['PostLength', 'Hashtags', 'Mentions']])
    scale_numeric = pd.DataFrame(scale_numeric, columns=['PostLength', 'Hashtags', 'Mentions'])
    final_set = preproc.combine_normalised(scale_numeric, transformed_test).drop('Totalengagement2', axis=1)
    final_set.Format = pd.to_numeric(final_set.Format)

    prediction = xgmodel.predict(final_set)
    output = pd.concat([df[['Account', 'Format', 'Postlength', 'Hashtags', 'Mentions']].reset_index(drop=True),
                        pd.DataFrame(prediction, columns=["Expected_Engagement"])], axis=1)
    output = output.groupby(['Account', 'Format']).max().reset_index()
    postFormat = output.groupby(['Format']).max().reset_index()
    postFormat['Percent'] = round((postFormat['Expected_Engagement'] / postFormat['Expected_Engagement'].sum()) * 100,
                                  2)
    output.Expected_Engagement = output.Expected_Engagement.apply(round)
    predicted_values = output[output.Expected_Engagement == max(output.Expected_Engagement)]

    def detailed_stats(infile, chanell='Facebook'):
        if chanell == 'Twitter':
            infile = infile.query("Account == '{}'".format(chanell))
            infile.Postlength = np.where(infile.Postlength > 280, infile.Postlength - randint(95, 100),
                                         infile.Postlength)
        else:
            infile = infile.query("Account == '{}'".format(chanell))
        json_records = infile.to_json(orient='records')
        data = []
        data = json.loads(json_records)

        return data

    pf = json.loads(postFormat.query('Format != "0"')[['Format', 'Expected_Engagement', 'Percent']].to_json(orient='records'))

    context = {
        'bet_params': {
            'platform': predicted_values.Account.values[0].lower,
            'format': predicted_values.Format.values[0],
            'postlength': predicted_values.Postlength.values[0],
            'hashtags': predicted_values.Hashtags.values[0],
            'engagement': round(predicted_values.Expected_Engagement.values[0]),
            'mentions': predicted_values.Mentions.values[0]},
        'pie_chart': {
            'pie_labels': list(postFormat['Format']),
            'pie_values': list(postFormat['Expected_Engagement']),
            'pie_values2': pf,
        },
        'facebook': detailed_stats(infile=output, chanell='Facebook'),
        'twitter': detailed_stats(infile=output, chanell='Twitter'),
        'linkedin': detailed_stats(infile=output, chanell='LinkedIn'),
    }

    return render(request, 'dashboard/nba.html', context)
