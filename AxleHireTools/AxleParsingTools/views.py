import pandas as pd
from django.shortcuts import render
from django.http import FileResponse, Http404
from AxleParsingTools.utils import utils


# Create your views here.
def axle_hire_index(request):
    return render(request, "index.html")


def parse_data(request):
    status = ''
    policy = request.POST.get('policy')
    claim_csv_src = request.FILES.get('claim_csv')
    all_report_zip_src = request.FILES.get('all_report_zip_file')

    utils.save_file(src=claim_csv_src, dst='cache/claim.csv')
    utils.save_file(src=all_report_zip_src, dst='cache/all.zip')

    all_report_df = utils.get_all_report(zip_src='cache/all.zip')

    ending_df = pd.read_csv('AxleParsingTools/utils/files/ending_wednesday.csv')
    claim_df = pd.read_csv('cache/claim.csv')

    res_df = utils.process_all(ending_df, claim_df, all_report_df, policy)
    res_df.to_csv('cache/res.csv', index=False)

    status = '解析成功！'
    return render(request, "download_result.html", {'status': status, 'download': 'yes'})


def download(request):
    try:
        response = FileResponse(open('cache/res.csv', 'rb'))
        return response
    except:
        return Http404