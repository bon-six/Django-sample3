import graphene
from graphene_django import DjangoObjectType
from graphql import GraphQLError
from django.db.models import Q

from .models import Link, Vote
from users.schema import UserType


class LinkType(DjangoObjectType):
    class Meta:
        model = Link
        fields = '__all__'

class VoteType(DjangoObjectType):
    class Meta:
        model = Vote
        fields = '__all__'

class Query(graphene.ObjectType):
    links = graphene.List(
        LinkType, 
        search=graphene.String(),
        first=graphene.Int(),
        skip=graphene.Int()
    )
    link_by_id = graphene.Field(LinkType, id=graphene.Int())
    votes = graphene.List(VoteType)

    def resolve_links(self, info, search=None, first=None, skip=None, **kwargs):
        print(info.context.body)
        qs = Link.objects.all()

        if search:
            filter = (
                Q(url__icontains=search) |
                Q(description__icontains=search)
            )
            qs = qs.filter(filter)
        
        if skip:
            qs = qs[skip:]

        if first:
            qs = qs[:first]

        return qs

    def resolve_link_by_id(self, info, id):
        return Link.objects.get(pk=id)

    def resolve_votes(self, info, **kwargs):
        return Vote.objects.all()

class CreateLink(graphene.Mutation):
    id = graphene.Int()
    url = graphene.String()
    description = graphene.String()
    posted_by = graphene.Field(UserType)

    class Arguments:
        url = graphene.String()
        description = graphene.String()

    def mutate(self, info, url, description):
        user = info.context.user or None
        link = Link(
            url=url, 
            description=description, 
            posted_by=user
        )
        link.save()
        return CreateLink(
            id = link.id,
            url = link.url,
            description = link.description,
            posted_by = link.posted_by
        )

class UpdateLink(graphene.Mutation):
    link = graphene.Field(LinkType)

    class Arguments():
        link_id = graphene.Int()
        url = graphene.String()
        description = graphene.String()

    def mutate(self, info, link_id, url, description):
        user = info.context.user
        if user.is_anonymous:
            raise GraphQLError("You must logged in in order to update links you posted")

        link = Link.objects.filter(pk=link_id).first()
        if not link:
            raise Exception("The Link ID specified does not exist")
        if link.posted_by:
            if user != link.posted_by:  # auth.models.User object comparison
                raise GraphQLError("You must be same user who posted in order to update")
        else:
            print(f"***INFO***: {user} updated {link.url} which creator is null")

        link.url = url
        link.description = description
        link.posted_by = user
        link.save()
        return UpdateLink(link=link)

class DeleteLink(graphene.Mutation):
    ok = graphene.Boolean()

    class Arguments():
        link_id = graphene.Int()

    def mutate(self, info, link_id):
        user = info.context.user
        if user.is_anonymous:
            raise GraphQLError("You must logged in in order to delete links you posted")

        link = Link.objects.filter(pk=link_id).first()
        if not link:
            raise Exception("The Link ID specified does not exist")
        if link.posted_by:
            if user != link.posted_by:  # auth.models.User object comparison
                raise GraphQLError("You must be same user who posted in order to delete")
        else:
            print(f"***INFO***: {user} deleted {link.url} which creator is null")

        link.delete()
        return DeleteLink(ok=True)

class CreateVote(graphene.Mutation):
    user = graphene.Field(UserType)
    link = graphene.Field(LinkType)

    class Arguments:
        link_id = graphene.Int()

    def mutate(self, info, link_id):
        user = info.context.user
        if user.is_anonymous:
            raise GraphQLError ("You must be logged in in order to vote!")
        
        link = Link.objects.filter(id=link_id).first()
        if not link:
            raise Exception("Invalid link id")

        Vote.objects.create(
            user=user,
            link=link
        )

        return CreateVote(user=user, link=link)

class Mutation(graphene.ObjectType):
    create_link = CreateLink.Field()
    create_vote = CreateVote.Field()
    update_link = UpdateLink.Field()
    delete_link = DeleteLink.Field()