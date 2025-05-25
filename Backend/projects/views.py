from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework import status
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404

from .models import Firm,FirmMembership,Tasks, Invites


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
            firm = firm,
            member = request.user
        )

        return Response({
            "id": firm.id,
            "name": firm.name,
            "description": firm.description,
            "owner": firm.owner.username
        }, status=status.HTTP_201_CREATED)

class EditFirm(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]  # Allows image upload

    def patch(self, request, firm_id):
        firm = get_object_or_404(Firm, id=firm_id)

        if firm.owner != request.user:
            return Response({"detail": "Forbidden – only the owner can edit the firm."},
                            status=status.HTTP_403_FORBIDDEN)

        name        = request.data.get("name")
        description = request.data.get("description")
        image       = request.FILES.get("image")

        if name:
            firm.name = name
        if description is not None:
            firm.description = description
        if image:
            firm.logo = image

        firm.save()

        return Response({
            "id": firm.id,
            "name": firm.name,
            "description": firm.description,
            "owner": firm.owner.username,
            "image": request.build_absolute_uri(firm.logo.url) if firm.logo else None,
        }, status=status.HTTP_200_OK)

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
                "owner_picture": request.build_absolute_uri(firm.owner.profile_picture.url) if firm.owner.profile_picture else None,
                "logo": request.build_absolute_uri(firm.logo.url) if firm.logo else None,
                "joined": membership.joined,
            })
        return Response(data, status=200)
    
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

    def get(self, request):
        firm = request.query_params.get('firm')
        all  = request.query_params.get('all')
        if not firm:
            return Response({"error": "Missing 'firm' parameter"}, status=status.HTTP_400_BAD_REQUEST)

        if all != "Y":
            members = FirmMembership.objects.filter(firm__name=firm).select_related("member")
            data = [{
                "id": m.member.id,
                "username": m.member.username,
                "relation": "member",
                "profile_picture": request.build_absolute_uri(m.member.profile_picture.url) if m.member.profile_picture else None
            } for m in members]
            return Response(data, status=status.HTTP_200_OK)

        owner_firm = Firm.objects.filter(name=firm, owner=request.user).first()
        if owner_firm is None:
            return Response({"error": "You do not own this firm"}, status=status.HTTP_400_BAD_REQUEST)

        firm_member_ids = set(
            FirmMembership.objects.filter(firm=owner_firm)
                                  .values_list("member_id", flat=True)
        )

        invited_ids = set(
            Invites.objects.filter(firm=owner_firm)
                           .values_list("sent_to_id", flat=True)
        )

        data = []
        for user in User.objects.all():
            if user.id in firm_member_ids:
                relation = "member"
            elif user.id in invited_ids:
                relation = "invited"
            else:
                relation = "normal"

            data.append({
                "id": user.id,
                "username": user.username,
                "relation": relation,
                "profile_picture": request.build_absolute_uri(user.profile_picture.url) if user.profile_picture else None
            })

        return Response(data, status=status.HTTP_200_OK)


class KickMember(APIView):

    permission_classes = [IsAuthenticated]

    def delete(self, request):
        membership_id = request.data.get("membership_id")
        if not membership_id:
            return Response({"detail": "membership_id is required"}, status=400)

        membership = get_object_or_404(FirmMembership, pk=membership_id)

        firm = membership.firm
        if firm.owner != request.user:
            return Response({"detail": "Forbidden – only the firm owner can kick members"},
                            status=status.HTTP_403_FORBIDDEN)

        # Prevent owner from kicking themselves through this endpoint
        if membership.member == request.user:
            return Response({"detail": "Owner cannot remove themselves"}, status=400)

        membership.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    

class AssignTask(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]          # accept files

    def post(self, request):
        user_id      = request.data.get("user")
        firm_id = request.data.get("firm_id")
        name         = request.data.get("name")
        description  = request.data.get("description")
        attachment   = request.FILES.get("attachment")      # may be None

        if not all([user_id, name, description]):
            return Response({"detail": "user, name and description are required"},
                            status=status.HTTP_400_BAD_REQUEST)

        requester_membership = get_object_or_404(
            FirmMembership, member=request.user, firm_id=firm_id
        )
        if not requester_membership:
            return Response({"detail": "You are not in any firm."}, status=403)

        member = get_object_or_404(
            FirmMembership, member_id=user_id, firm_id=firm_id
        )
        if not member:
            return Response({"detail": "User not in your firm."}, status=404)

        task = Tasks.objects.create(
            user_details=member,
            name=name,
            description=description,
            attachment=attachment,
        )

        return Response(
            {
                "id": task.id,
                "name": task.name,
                "description": task.description,
                "status": task.status,
                "attachment": request.build_absolute_uri(task.attachment.url) if task.attachment else None,
                "user": task.user_details.id,
            },
            status=201,
        )


class GetAllTaskMember(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        member = request.user

        # Get all FirmMembership entries for this user
        memberships = FirmMembership.objects.filter(member=member).select_related("firm")

        # Filter tasks by those memberships
        tasks = Tasks.objects.filter(user_details__in=memberships).select_related("user_details__member", "user_details__firm")

        data = [{
            "task_id":    t.id,
            "task_name":  t.name,
            "description":t.description,
            "contents":   t.contents,
            "status":     t.status,
            "attachment": request.build_absolute_uri(t.attachment.url) if t.attachment else None,
            "owner":      t.user_details.member.username,
            "firm":       t.user_details.firm.name
        } for t in tasks]

        return Response(data, status=200)



class GetAllTasksForFirm(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        firm_id = request.query_params.get("firm_id")
        if not firm_id:
            return Response({"error": "Missing 'firm_id' parameter"}, status=400)

        # Check if user is part of the firm (safety)
        if not FirmMembership.objects.filter(firm_id=firm_id, member=request.user).exists():
            return Response({"detail": "You are not a member of this firm"}, status=403)

        tasks = Tasks.objects.filter(user_details__firm_id=firm_id) \
                             .select_related("user_details__member")

        data = [{
            "task_id":   t.id,
            "task_name": t.name,
            "description": t.description,
            "contents":   t.contents,
            "status":     t.status,
            "attachment": request.build_absolute_uri(t.attachment.url) if t.attachment else None,
            "assigned_to": t.user_details.member.username
        } for t in tasks]

        return Response(data, status=200)

class EditTask(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def patch(self, request, pk):
        task = get_object_or_404(Tasks, pk=pk)
        if task.user_details.member != request.user:
            return Response({"detail": "Forbidden"}, status=403)

        allowed_json = {"name", "description", "contents", "status"}
        attachment   = request.FILES.get("attachment")


        # JSON fields
        for field in allowed_json:
            if field in request.data:
                setattr(task, field, request.data[field])

        # file field (optional)
        if attachment:
            task.attachment = attachment

        # status validation
        if "status" in request.data:
            valid_statuses = {c[0] for c in Tasks.STATUS_CHOICES}
            if task.status not in valid_statuses:
                return Response({"detail": f"status must be one of {', '.join(valid_statuses)}"},
                                status=400)
        task.save()

        return Response(
            {
                "id": task.id,
                "name": task.name,
                "description": task.description,
                "contents": task.contents,
                "status": task.status,
                "attachment": request.build_absolute_uri(task.attachment.url) if task.attachment else None,
                "user": task.user_details.id,
            },
            status=200,
        )


class DeleteTask(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, pk):
        task = get_object_or_404(Tasks, pk=pk)

        if task.user_details.member != request.user:
            return Response({"detail": "Forbidden"}, status=status.HTTP_403_FORBIDDEN)

        task.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
class SendInvite(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        recipient_id = request.data.get("recipient")

        if not recipient_id:
            return Response({"detail": "Missing 'recipient' field"}, status=400)

        # Check if the recipient exists (for debug)
        recipient = User.objects.filter(pk=recipient_id).first()
        if not recipient:
            return Response({"detail": "User not found"}, status=404)

        firm = Firm.objects.filter(owner=request.user).first()
        if not firm:
            return Response({"detail": "Firm not found"}, status=404)

        invite = Invites.objects.create(
            sent_to=recipient,
            sent_from=request.user,
            firm=firm
        )

        return Response(
            {
                "id": invite.id,
                "sent_to": invite.sent_to.username,
                "sent_from": invite.sent_from.username,
                "sent_time": invite.sent_time,
            },
            status=201
        )

class GetMyInvites(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        invites = Invites.objects.filter(sent_to=request.user).select_related("sent_from")

        data = []
        for invite in invites:
            data.append({
                "invite_id": invite.id,
                "sent_from_id": invite.sent_from.id,
                "sent_from_username": invite.sent_from.username,
                "sent_from_picture": request.build_absolute_uri(invite.sent_from.profile_picture.url) if invite.sent_from.profile_picture else None,
                "sent_time": invite.sent_time,
            })

        return Response(data, status=status.HTTP_200_OK)
    
class AcceptInvite(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):

        invite_id = request.data.get("invite_id")

        if not invite_id:
            return Response({"detail": "invite_id is required"}, status=400)

        invite = get_object_or_404(
            Invites, pk=invite_id, sent_to=request.user
        )

        firm = invite.firm
        if not firm:
            return Response({"detail": "Firm not found"}, status=404)

        # Create membership if it doesn't already exist
        membership, created = FirmMembership.objects.get_or_create(
            firm=firm,
            member=request.user,
        )

        # Delete the invite
        invite.delete()

        return Response(
            {
                "membership_id": membership.id,
                "firm_id": firm.id,
                "firm_name": firm.name,
                "joined": membership.joined,
                "was_created": created,   # False if membership already existed
            },
            status=status.HTTP_201_CREATED,
        )

    
class RejectInvite(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request):

        invite_id = request.data.get("invite_id")
        if not invite_id:
            return Response({"detail": "invite_id is required"}, status=400)

        invite = get_object_or_404(
            Invites,
            pk=invite_id,
            sent_to=request.user
        )

        invite.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    

