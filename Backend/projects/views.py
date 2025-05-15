from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.contrib.auth import get_user_model
from .models import Firm,FirmMembership


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
    def post(self,request):
        user = request.query_params.get('user')
        description = request.query_params.get('description')
    

    

