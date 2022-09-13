from django.shortcuts import render
from .models import Subject, Student, Apply

class AdminPage:
    def __init__(self, request):
        self.request = request
        self.adminUser = str(request.user)
    
    def index(self):
        return render(self.request, 'admin_view/index.html', {  
            "user": self.adminUser
        })

    def search(self):
        search_id_sj = ""
        if self.request.method == "POST":
            search_id_sj = self.request.POST['search_id_sj']
        return render(self.request, "admin_view/search.html", {
            "subjects": Subject.objects.all(),
            "search_id_sj": search_id_sj,
        })

    def checkStu(self):
        if self.request.method == "POST":
            subject = Subject.objects.get(pk=self.request.POST['subject'])
            print(subject)
            list_students = subject.sub_apply.all() 
        return render(self.request, "admin_view/checkStu.html", {
            "students": Student.objects.all(),
            "subject": subject,
            "list_students" : list_students,
        })
    
    def checkSub(self):
        if self.request.method == "POST":
            student = Student.objects.get(pk=self.request.POST['student'])
            list_subjects = student.stu_apply.all()
        return render(self.request, "admin_view/checkSub.html", {
            "subject": Subject.objects.all(),
            "student": student,
            "list_subjects": list_subjects
        })
    
    def student(self):
        search_username = ""
        if self.request.method == "POST":
            search_username = self.request.POST['search_username']
        return render(self.request, "admin_view/student.html", {
            "students": Student.objects.all(),
            "search_username": search_username,
        })

class StudentPage:
    def __init__(self, request):
        self.request = request
        self.user = Student.objects.get(pk=request.user)
    
    def index(self):
        return render(self.request, 'reg/index.html', {  
            "student": self.user
        })

    def search(self):
        search_sub = ""
        if self.request.POST.get('search_subject'):
            search_sub = self.request.POST['search_subject']
        return render(self.request, 'reg/search.html', {
            "student": self.user,
            "subjects": Subject.objects.all(),
            "search_subject": search_sub,
        })

    def status(self):
        applys = self.user.stu_apply.filter(status='complete')
        return render(self.request, 'reg/status.html', {
            "student": self.user,
            "applys": applys,
        })
    
    def quota(self):
        search_subject = ""
        applys = self.user.stu_apply.all()

        if self.request.POST.get('add'):
            subject = Subject.objects.get(pk=self.request.POST['add'])
            subject_add = Apply(student=self.user, subject=subject, status="add")
            subject_add.save()
        
        if self.request.POST.get('withdraw'):
            subject = Subject.objects.get(pk=self.request.POST['withdraw'])
            subject_withdraw = Apply.objects.get(student=self.user, subject=subject)
            subject_withdraw.status = "withdraw"
            subject_withdraw.save()

        if self.request.POST.get('cancel'):
            subject = Subject.objects.get(pk=self.request.POST['cancel'])
            subject_cancel = Apply.objects.get(student=self.user, subject=subject)
            if subject_cancel.status == "add":
                subject_cancel.delete()
            elif subject_cancel.status == "withdraw":
                subject_cancel.status = "add"
                subject_cancel.save()
            
        if self.request.POST.get('search_subject'):
            search_subject = self.request.POST['search_subject']
        
        if self.request.POST.get('submit'):
            search_subject = ""
            check_submit = True
            for apply in Apply.objects.filter(student=self.user):
                if apply.status == 'add':
                    tmp_subject = apply.subject
                    if tmp_subject.status == "N":
                        apply.delete()

                        apply.status = 'cantapp'
                        check_submit = False

            if check_submit:
                for apply in Apply.objects.filter(student=self.user):
                    if apply.status == 'add':
                        tmp_subject = apply.subject
                        tmp_subject.seat += 1
                        if tmp_subject.seat == tmp_subject.max_seat:
                            tmp_subject.status = "N"
                        tmp_subject.save()

                        apply.status = "complete"
                        apply.save()
                    elif apply.status == 'withdraw':
                        tmp_subject = apply.subject
                        tmp_subject.seat -= 1
                        tmp_subject.status = "Y"
                        tmp_subject.save()
                        apply.delete()
            return self.status()

        add_apply = Apply.objects.filter(student=self.user, status='add')
        withdraw_apply = Apply.objects.filter(student=self.user, status='withdraw')
        complete_apply = Apply.objects.filter(student=self.user, status='complete')

        add_list = [subject.subject_id for subject in add_apply]
        withdraw_list = [subject.subject_id for subject in withdraw_apply]
        complete_list = [subject.subject_id for subject in complete_apply]

        return render(self.request, 'reg/quota.html', {
            "student": self.user,
            "subjects": Subject.objects.all(),
            "search_subject": search_subject,
            "applys": applys,
            "complete_apply": complete_apply,
            "add_apply": add_apply,
            "withdraw_apply": withdraw_apply,
            "add_list": add_list,
            "withdraw_list": withdraw_list,
            "complete_list": complete_list,
        })