from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.contrib.auth import get_user_model
from .models import Firm,FirmMembership,Tasks
from django.shortcuts import get_object_or_404


User = get_user_model()

class CreateFirm(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        name = request.query_params.get('name')
        description = request.query_params.get('description', '')

        if not name:
            return Response({"error": "Missing 'name' parameter"}, status=status.HTTP_400_BAD_REQUEST)

        firm = Firm.objects.create(
            name=name,
            description=description,
            owner=request.user
        )
        FirmMembership.objects.create(
            firm = name,
            member = request.user
        )

        return Response({
            "id": firm.id,
            "name": firm.name,
            "description": firm.description,
            "owner": firm.owner.username
        }, status=status.HTTP_201_CREATED)

class DeleteFirm(APIView):
    def delete(self, request, firm_id):
        try:
            firm = Firm.objects.get(id=firm_id, owner=request.user)
            firm.delete()
            return Response(status=204)
        except Firm.DoesNotExist:
            return Response({"error": "Not found"}, status=404)
        
    
class GetMemberFirms(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.query_params.get('user')

        if not user:
            return Response({"error": "Missing 'user' parameter"}, status=status.HTTP_400_BAD_REQUEST)

        memberships = FirmMembership.objects.filter(member__username=user).select_related("firm")
        data = []
        for membership in memberships:
            firm = membership.firm
            data.append({
                "firm_id": firm.id,
                "firm_name": firm.name,
                "description": firm.description,
                "owner": firm.owner.username,
                "joined": membership.joined,
            })
        return data
    
class GetSingleFirm(APIView):
    permission_classes = [IsAuthenticated]
    def get(self,request):
        name = request.query_params.get('name')
        if not name:
            return Response({"error": "Missing 'name' parameter"}, status=status.HTTP_400_BAD_REQUEST)
        firm =  Firm.objects.filter(name=name)
        return Response({
            "id": firm.id,
            "name": firm.name,
            "description": firm.description,
            "owner": firm.owner.username
        }, status=status.HTTP_200_OK)
    
class GetMembers(APIView):
    permission_classes = [IsAuthenticated]
    def get(self,request):
        firm = request.query_params.get('firm')
        all = request.query_params.get('all')
        if not firm:
            return Response({"error": "Missing 'firm' parameter"}, status=status.HTTP_400_BAD_REQUEST)
        if all == "Y":
         members = User.objects.all()
        else:
         members =  FirmMembership.objects.filter(firm=firm)
        return Response(members, status=status.HTTP_200_OK)
    

class AssignTask(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user_id = request.data.get("user")
        name = request.data.get("name")
        description = request.data.get("description")

        if not all([user_id, name, description]):
            return Response(
                {"detail": "user, name and description are required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        member = FirmMembership.objects.filter(pk=user_id).first()
        if member is None:
            return Response(
                {"detail": "User not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        task = Tasks.objects.create(
            user_details=member,
            name=name,
            description=description,
        )

        return Response(
            {
                "id": task.id,
                "name": task.name,
                "description": task.description,
                "status": task.status,
                "user": task.user_details.id,
            },
            status=status.HTTP_201_CREATED,
        )

class GetAllTaskMember(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        name = request.data.get("name")
        if not name:
            return Response({"error": "Missing 'name' parameter"}, status=status.HTTP_400_BAD_REQUEST)
        
        tasks = Tasks.objects.filter(name=name)
        data = []
        for task in tasks:
            data.append({
                "task_id": task.id,
                "task_name": task.name,
                "description": task.description,
                "contents": task.contents,
                "status": task.status,
                "owner": task.user_details.username,
            })
        return data
    

class EditTask(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, pk):
 
        task = get_object_or_404(Tasks, pk=pk)

        if task.user_details.member != request.user:
            return Response({"detail": "Forbidden"}, status=status.HTTP_403_FORBIDDEN)

        allowed = {"name", "description", "contents", "status"}
        invalid_keys = set(request.data) - allowed
        if invalid_keys:
            return Response(
                {"detail": f"Invalid field(s): {', '.join(invalid_keys)}"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        
        if "status" in request.data:
            valid_statuses = {choice[0] for choice in Tasks.STATUS_CHOICES}
            if request.data["status"] not in valid_statuses:
                return Response(
                    {"detail": f"status must be one of {', '.join(valid_statuses)}"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        for field in allowed:
            if field in request.data:
                setattr(task, field, request.data[field])

        task.save()

        return Response(
            {
                "id": task.id,
                "name": task.name,
                "description": task.description,
                "contents": task.contents,
                "status": task.status,
                "user": task.user_details.id,
            },
            status=status.HTTP_200_OK,
        )


class DeleteTask(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, pk):
        task = get_object_or_404(Tasks, pk=pk)
        
        if task.user_details.member != request.user:
            return Response({"detail": "Forbidden"}, status=status.HTTP_403_FORBIDDEN)

        task.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    

    

