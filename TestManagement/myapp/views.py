import sqlite3
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from .forms import LoginForm, TestTypeForm, TestFilterForm, CreateTestRequest, FilterTestRequestForm
import datetime
from django.utils import timezone
from django.http import JsonResponse
# Create your views here.

def login_view(request):

    form = LoginForm(request.POST or None)
    if request.method == "POST":
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('home')
            else:
                form.add_error(None, "Yanlış kullanıcı adı veya şifre!")

    return render(request, r'myapp/login.html', {'form': form})


def testrequest_view(request):

    form = CreateTestRequest(request.POST or None)
    if request.method == "POST":
        if form.is_valid():

            username = str(request.user)
            date = timezone.localdate().strftime("%d.%m.%Y")
            komponent = form.cleaned_data.get('komponent')
            aciklama = form.cleaned_data.get('aciklama')
            model = form.cleaned_data.get('model')
            marka = form.cleaned_data.get('marka')

            conn = sqlite3.connect(r'myapp/databases/Test_Requests.db')
            cursor = conn.cursor()
            cursor.execute('''INSERT INTO Test_Requests(Talep_Eden,Tarih,Açıklama,Komponent,Marka,Model) 
                           VALUES (?, ?, ?, ?, ?, ?)''',
                           (username, date, aciklama, komponent, marka, model))
            conn.commit()
            conn.close()
            return redirect('home')


        else:
            form = CreateTestRequest()

    return render(request, 'myapp/test_requests.html', {'form': form})

@login_required
def home_view(request):
    date_time_now = datetime.datetime.now()

    return render(request, 'myapp/home.html', {'current_time': date_time_now})


def tests_view(request):
    test_datas = []
    table_header = "Kayıtları görüntülemek için lütfen bir test türü seçiniz."
    form = TestTypeForm()
    filter_form = TestFilterForm()

    if request.method == 'POST':
        if 'apply_button' in request.POST:
            form = TestTypeForm(request.POST)
            if form.is_valid():
                test_type = form.cleaned_data['test_type']
                request.session['test_type'] = test_type

                if test_type == 'elektriksel':
                    table_header = "Elektriksel Güvenlik Testleri"
                    conn = sqlite3.connect(r'myapp/databases/Electrical_tests.db')
                    cursor = conn.cursor()
                    cursor.execute('SELECT name FROM sqlite_master WHERE type="table" AND name="ElectricalTestLog"')
                    table_exist = cursor.fetchone()
                    if not table_exist:
                        cursor.execute('''CREATE TABLE ElectricalTestLog(
                        Talep_Eden TEXT NOT NULL,
                        Komponentin_Adı TEXT NOT NULL,
                        Testin_Adı TEXT NOT NULL,
                        SONUÇ BLOB TEXT NULL,
                        Talep_Tarihi TEXT NOT NULL,
                        Testin_Yapılma_Tarihi TEXT NOT NULL,
                        Test_Raporu TEXT NOT NULL,
                        Marka TEXT NOT NULL,
                        Model TEXT NOT NULL,
                        Açıklama TEXT NOT NULL
                        )
                        ''')
                    cursor.execute('SELECT * FROM ElectricalTestLog ORDER BY Talep_Tarihi DESC')
                    test_datas = cursor.fetchall()
                    conn.close()

                elif test_type == 'malzeme':
                    table_header = "Malzeme Testleri"
                    conn = sqlite3.connect(r'myapp/databases/Material_tests.db')
                    cursor = conn.cursor()
                    cursor.execute('SELECT name FROM sqlite_master WHERE type="table" AND name="MaterialTestLog"')
                    table_exist = cursor.fetchone()
                    if not table_exist:
                        cursor.execute('''CREATE TABLE MaterialTestLog(
                                        Talep_Eden TEXT NOT NULL,
                                        Komponentin_Adı TEXT NOT NULL,
                                        Testin_Adı TEXT NOT NULL,
                                        SONUÇ TEXT NOT NULL,
                                        Talep_Tarihi TEXT NOT NULL,
                                        Testin_Yapılma_Tarihi TEXT NOT NULL,
                                        Test_Raporu TEXT NOT NULL,
                                        Marka TEXT NOT NULL,
                                        Model TEXT NOT NULL,
                                        Açıklama TEXT NOT NULL 
                                        )
                                        ''')
                    cursor.execute('SELECT * FROM MaterialTestLog ORDER BY Talep_Tarihi DESC')
                    test_datas = cursor.fetchall()
                    conn.close()

        elif 'filter_button' in request.POST:
            filter_form = TestFilterForm(request.POST)
            if filter_form.is_valid():
                test_type = request.session.get('test_type')
                if test_type == 'elektriksel':
                    table_header = "Elektriksel Güvenlik Testleri"
                    requester = filter_form.cleaned_data.get('requester')
                    requested_date = filter_form.cleaned_data.get('requested_date')
                    test_name = filter_form.cleaned_data.get('test_name')
                    component = filter_form.cleaned_data.get('component')
                    brand = filter_form.cleaned_data.get('brand')
                    model = filter_form.cleaned_data.get('model')
                    result = filter_form.cleaned_data.get('result')
                    explanation = filter_form.cleaned_data.get('explanation')

                    conn_filter = sqlite3.connect(r'myapp/databases/Electrical_tests.db')
                    filter_cursor = conn_filter.cursor()
                    filter_query = '''
                    SELECT * FROM ElectricalTestLog
                    WHERE Talep_Eden LIKE ? COLLATE NOCASE
                    AND Komponentin_Adı LIKE ? COLLATE NOCASE
                    AND Testin_Adı LIKE ? COLLATE NOCASE
                    AND SONUÇ LIKE ? COLLATE NOCASE
                    AND Talep_Tarihi LIKE ? COLLATE NOCASE
                    AND Marka LIKE ? COLLATE NOCASE
                    AND Model LIKE ? COLLATE NOCASE
                    AND Açıklama LIKE ? COLLATE NOCASE ORDER BY Talep_Tarihi DESC
                    '''
                    filter_parameter = (
                        f"%{requester}%", f"%{component}%", f"%{test_name}%",
                        f"%{result}%", f"%{requested_date}%", f"%{brand}%",
                        f"%{model}%", f"%{explanation}%"
                    )
                    filter_cursor.execute(filter_query, filter_parameter)
                    test_datas = filter_cursor.fetchall()
                    conn_filter.close()

                elif test_type == 'malzeme':
                    table_header = "Malzeme Testleri"
                    requester = filter_form.cleaned_data.get('requester')
                    requested_date = filter_form.cleaned_data.get('requested_date')
                    test_name = filter_form.cleaned_data.get('test_name')
                    component = filter_form.cleaned_data.get('component')
                    brand = filter_form.cleaned_data.get('brand')
                    model = filter_form.cleaned_data.get('model')
                    result = filter_form.cleaned_data.get('result')
                    explanation = filter_form.cleaned_data.get('explanation')

                    conn_filter = sqlite3.connect(r'myapp/databases/Material_tests.db')
                    filter_cursor = conn_filter.cursor()
                    filter_query = '''
                    SELECT * FROM MaterialTestLog
                    WHERE Talep_Eden LIKE ?
                    AND Komponentin_Adı LIKE ?
                    AND Testin_Adı LIKE ?
                    AND SONUÇ LIKE ?
                    AND Talep_Tarihi LIKE ?
                    AND Marka LIKE ?
                    AND Model LIKE ?
                    AND Açıklama LIKE ? ORDER BY Talep_Tarihi DESC
                    '''
                    filter_parameter = (
                        f"%{requester}%", f"%{component}%", f"%{test_name}%",
                        f"%{result}%", f"%{requested_date}%", f"%{brand}%",
                        f"%{model}%", f"%{explanation}%"
                    )
                    filter_cursor.execute(filter_query, filter_parameter)
                    test_datas = filter_cursor.fetchall()
                    conn_filter.close()

        elif 'delete_button' in request.POST:
            test_type = request.session.get('test_type')
            if test_type == 'malzeme':
                conn_clear = sqlite3.connect(r'myapp/databases/Material_tests.db')
                cursor_clear = conn_clear.cursor()
                cursor_clear.execute("SELECT * FROM MaterialTestLog ORDER BY Talep_Tarihi DESC")
                test_datas = cursor_clear.fetchall()
                conn_clear.close()
            elif test_type == 'elektriksel':
                conn_clear = sqlite3.connect(r'myapp/databases/Electrical_tests.db')
                cursor_clear = conn_clear.cursor()
                cursor_clear.execute("SELECT * FROM ElectricalTestLog ORDER BY Talep_Tarihi DESC")
                test_datas = cursor_clear.fetchall()
                conn_clear.close()

    return render(request, 'myapp/tests.html', {
        'form': form,
        'test_datas': test_datas,
        'table_header': table_header,
        'filter_form': filter_form,
    })

def test_request_filter_view(request):
    full_request_datas = []
    filter_form = FilterTestRequestForm(request.POST or None)
    if 'filter_button' in request.POST:
        if request.method == 'POST':
            if filter_form.is_valid():
                filtreleme_tarihi = filter_form.cleaned_data.get('filtreleme_tarihi')
                marka = filter_form.cleaned_data.get('marka')
                model = filter_form.cleaned_data.get('model')
                komponent = filter_form.cleaned_data.get('komponent')
                requester = filter_form.cleaned_data.get('requester')

                conn = sqlite3.connect(r'myapp/databases/Test_Requests.db')
                cursor = conn.cursor()
                cursor.execute('''SELECT * FROM Test_Requests where Tarih LIKE ? COLLATE NOCASE
                                        AND Talep_Eden LIKE ? COLLATE NOCASE 
                                        AND Komponent LIKE ? COLLATE NOCASE
                                        AND Marka LIKE ? COLLATE NOCASE
                                        AND Model LIKE ? COLLATE NOCASE
                                        ORDER BY Tarih DESC''', (f"%{filtreleme_tarihi}", f"%{requester}%", f"%{komponent}%",
                                                                 f"%{marka}%", f"%{model}%"))
                full_request_datas = cursor.fetchall()
                conn.close()
    else:
        conn = sqlite3.connect(r'myapp/databases/Test_Requests.db')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM Test_Requests ORDER BY Tarih DESC')
        full_request_datas = cursor.fetchall()
        conn.close()

    return render(request, r'myapp/test_requests_list.html', {'full_request_datas': full_request_datas, 'filter_form': filter_form})

def get_test_details(request):
    talep_eden = request.GET.get('talep_eden')
    komponent = request.GET.get('komponent')
    marka = request.GET.get('marka')
    model = request.GET.get('model')
    conn = sqlite3.connect(r'myapp/databases/Test_Requests.db')
    cursor = conn.cursor()
    cursor.execute('''SELECT * FROM Test_Requests
     WHERE Talep_Eden = ?
     AND Komponent = ?
     AND Marka = ?
     AND Model = ?''', (talep_eden, komponent, marka, model))
    data = cursor.fetchone()
    conn.close()

    response_data = {
        'talep_eden': data[0],
        'talep_tarihi': data[1],
        'açıklama': data[2],
        'komponent': data[3],
        'marka': data[4],
        'model': data[5],
    }
    return JsonResponse(response_data)
def add_to_calendar(request):
    if request.method == 'POST':
        talep_tarihi = request.POST.get('talep_tarihi')
        test_tarihi = ''
        talep_eden = request.POST.get('talep_eden')
        testin_adı = request.POST.get('testin_adı')
        komponent = request.POST.get('komponent')
        marka = request.POST.get('marka')
        model = request.POST.get('model')
        açıklama = request.POST.get('açıklama')
        sonuç = 'Tamamlanmadı'
        test_raporu = ''
        test_türü = request.POST.get('test_türü')

        if test_türü == 'elektriksel güvenlik':
            conn = sqlite3.connect(r'myapp/databases/Electrical_tests.db')
            table_name = "ElectricalTestLog"
        else:
            conn = sqlite3.connect(r'myapp/databases/Material_tests.db')
            table_name = "MaterialTestLog"
        cursor = conn.cursor()
        cursor.execute(f'''
            INSERT INTO {table_name} (Talep_Tarihi, Testin_Yapılma_Tarihi, Talep_Eden, Testin_Adı, Komponentin_Adı, Marka, Model, Açıklama, SONUÇ, Test_Raporu)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (talep_tarihi, test_tarihi, talep_eden, testin_adı, komponent, marka, model, açıklama, sonuç, test_raporu))
        conn.commit()
        conn.close()

        conn_request = sqlite3.connect(r'myapp/databases/Test_Requests.db')
        cursor_request = conn_request.cursor()
        query = '''DELETE FROM Test_Requests WHERE Talep_Eden=?
                    AND Tarih=?
                    AND Komponent=?
                    AND Marka=?
                    AND Model=?'''
        parameter = (talep_eden, talep_tarihi, komponent, marka, model)
        cursor_request.execute(query, parameter)
        conn_request.commit()
        conn_request.close()
        return redirect('home')

    return render(request, r'myapp/test_requests.html')


def getTestCalendarDetails(request):
    
    pass