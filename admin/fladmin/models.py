# Create your models here.
# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models
from django.contrib.postgres.fields import ArrayField
from django.contrib.contenttypes.models import ContentType

class ApiEvent(models.Model):
    id = models.UUIDField(primary_key=True)
    bot_id = models.BigIntegerField()
    events = models.TextField()  # This field type is a guess.

    class Meta:
        managed = False
        db_table = 'api_event'


class AuthGroup(models.Model):
    name = models.CharField(unique=True, max_length=150)

    class Meta:
        managed = False
        db_table = 'auth_group'


class AuthGroupPermissions(models.Model):
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)
    permission = models.ForeignKey('AuthPermission', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_group_permissions'
        unique_together = (('group', 'permission'),)


class AuthPermission(models.Model):
    name = models.CharField(max_length=255)
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING)
    codename = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'auth_permission'
        unique_together = (('content_type', 'codename'),)


class AuthUser(models.Model):
    password = models.CharField(max_length=128)
    last_login = models.DateTimeField(blank=True, null=True)
    is_superuser = models.BooleanField()
    username = models.CharField(unique=True, max_length=150)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    email = models.CharField(max_length=254)
    is_staff = models.BooleanField()
    is_active = models.BooleanField()
    date_joined = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'auth_user'


class AuthUserGroups(models.Model):
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_groups'
        unique_together = (('user', 'group'),)


class AuthUserUserPermissions(models.Model):
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    permission = models.ForeignKey(AuthPermission, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_user_permissions'
        unique_together = (('user', 'permission'),)


class BotCommands(models.Model):
    id = models.UUIDField(primary_key=True)
    slash = models.IntegerField(blank=True, null=True)
    name = models.TextField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    args = models.TextField(blank=True, null=True)  # This field type is a guess.
    examples = models.TextField(blank=True, null=True)  # This field type is a guess.
    premium_only = models.BooleanField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)  # This field type is a guess.
    doc_link = models.TextField(blank=True, null=True)
    bot_id = models.BigIntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'bot_commands'


class BotMaint(models.Model):
    id = models.UUIDField(primary_key=True)
    bot_id = models.BigIntegerField(blank=True, null=True)
    reason = models.TextField(blank=True, null=True)
    type = models.IntegerField(blank=True, null=True)
    epoch = models.BigIntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'bot_maint'


class BotPacks(models.Model):
    id = models.UUIDField(primary_key=True)
    icon = models.TextField(blank=True, null=True)
    banner = models.TextField(blank=True, null=True)
    created_at = models.BigIntegerField(blank=True, null=True)
    owner = models.BigIntegerField(blank=True, null=True)
    api_token = models.TextField(unique=True, blank=True, null=True)
    bots = models.TextField(blank=True, null=True)  # This field type is a guess.
    description = models.TextField(blank=True, null=True)
    name = models.TextField(unique=True, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'bot_packs'


class BotPromotions(models.Model):
    id = models.UUIDField(primary_key=True)
    bot_id = models.BigIntegerField(blank=True, null=True)
    title = models.TextField(blank=True, null=True)
    info = models.TextField(blank=True, null=True)
    css = models.TextField(blank=True, null=True)
    type = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'bot_promotions'


class BotReviews(models.Model):
    id = models.UUIDField(primary_key=True)
    bot_id = models.BigIntegerField()
    user_id = models.BigIntegerField()
    star_rating = models.FloatField(blank=True, null=True)
    review_text = models.TextField(blank=True, null=True)
    flagged = models.BooleanField(blank=True, null=True)
    replies = models.TextField(blank=True, null=True)  # This field type is a guess.
    epoch = models.TextField(blank=True, null=True)  # This field type is a guess.
    review_upvotes = models.TextField(blank=True, null=True)  # This field type is a guess.
    review_downvotes = models.TextField(blank=True, null=True)  # This field type is a guess.
    reply = models.BooleanField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'bot_reviews'


class BotStatsVotes(models.Model):
    bot_id = models.BigIntegerField(blank=True, null=True)
    total_votes = models.BigIntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'bot_stats_votes'


class BotStatsVotesPm(models.Model):
    bot_id = models.BigIntegerField(blank=True, null=True)
    votes = models.BigIntegerField(blank=True, null=True)
    epoch = models.BigIntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'bot_stats_votes_pm'


class BotVoter(models.Model):
    id = models.IntegerField(blank=True, primary_key = True)
    bot_id = models.BigIntegerField(blank=True)
    user_id = models.BigIntegerField(blank=True)
    timestamps = ArrayField(base_field = models.BigIntegerField(), blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'bot_voters'
        ordering = ['pk']

    def __str__(self):
        return f"{self.id}. BID: {self.bot_id}, UID: {self.user_id}"


class Bot(models.Model):
    bot_id = models.BigIntegerField(primary_key = True, editable = False)
    owner = models.BigIntegerField(blank=True, null=True)
    votes = models.BigIntegerField(blank=True, null=True)
    servers = models.BigIntegerField(blank=True, null=True)
    shard_count = models.BigIntegerField(blank=True, null=True)
    bot_library = models.TextField(blank=True, null=True)
    webhook = models.TextField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    long_description = models.TextField(blank=True, null=True)
    prefix = models.TextField(blank=True, null=True)
    api_token = models.TextField(unique=True, blank=True, null=True)
    website = models.TextField(blank=True, null=True)
    discord = models.TextField(blank=True, null=True)
    tags = ArrayField(base_field = models.TextField(), blank=False, null=False)
    certified = models.BooleanField(blank=True, null=True)
    queue = models.BooleanField(blank=True, null=True)
    banner = models.TextField(blank=True, null=True)
    created_at = models.BigIntegerField(blank=True, null=True)
    invite = models.TextField(blank=True, null=True)
    banned = models.BooleanField(blank=True, null=True)
    disabled = models.BooleanField(blank=True, null=True)
    github = models.TextField(blank=True, null=True)
    extra_owners = ArrayField(base_field = models.BigIntegerField(), blank=True, null=True) 
    features = ArrayField(base_field = models.TextField(), blank=True, null=True)
    private = models.BooleanField(blank=True, null=True)
    html_long_description = models.BooleanField(blank=True, null=True)
    invite_amount = models.IntegerField(blank=True, null=True)
    webhook_type = models.TextField(blank=True, null=True)
    user_count = models.BigIntegerField(blank=True, null=True)
    css = models.TextField(blank=True, null=True)
    shards = ArrayField(base_field = models.IntegerField(), blank=True, null=True)
    donate = models.TextField(blank=True, null=True)
    username_cached = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'bots'

    def __str__(self):
        return f"{self.username_cached} ({self.bot_id})"

class Servers(models.Model):
    guild_id = models.BigIntegerField(unique=True)
    votes = models.BigIntegerField(blank=True, null=True)
    webhook_type = models.TextField(blank=True, null=True)
    webhook = models.TextField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    long_description = models.TextField(blank=True, null=True)
    html_long_description = models.BooleanField(blank=True, null=True)
    css = models.TextField(blank=True, null=True)
    api_token = models.TextField(unique=True, blank=True, null=True)
    website = models.TextField(blank=True, null=True)
    tags = models.TextField(blank=True, null=True)  # This field type is a guess.
    certified = models.BooleanField(blank=True, null=True)
    created_at = models.BigIntegerField(blank=True, null=True)
    banned = models.BooleanField(blank=True, null=True)
    invite_amount = models.IntegerField(blank=True, null=True)
    user_provided_invite = models.BooleanField(blank=True, null=True)
    invite_code = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'servers'


class SupportRequests(models.Model):
    enquiry_type = models.TextField(blank=True, null=True)
    resolved = models.BooleanField(blank=True, null=True)
    files = models.TextField(blank=True, null=True)  # This field type is a guess.
    title = models.TextField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    bot_id = models.BigIntegerField(blank=True, null=True)
    id = models.UUIDField(primary_key=True)
    filenames = models.TextField(blank=True, null=True)  # This field type is a guess.

    class Meta:
        managed = False
        db_table = 'support_requests'


class Users(models.Model):
    user_id = models.BigIntegerField(blank=True, null=True)
    api_token = models.TextField(blank=True, null=True)
    vote_epoch = models.BigIntegerField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    certified = models.BooleanField(blank=True, null=True)
    badges = models.TextField(blank=True, null=True)  # This field type is a guess.
    username = models.TextField(blank=True, null=True)
    avatar = models.TextField(blank=True, null=True)
    css = models.TextField(blank=True, null=True)
    banned = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'users'


class Vanity(models.Model):
    type = models.IntegerField(blank=True, null=True)
    vanity_url = models.TextField(blank=True, unique=True)
    redirect = models.BigIntegerField(unique=True, blank=True, primary_key = True)
    redirect_text = models.TextField(unique=True, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'vanity'

    def __str__(self):
        base = f"{self.redirect}"
        if self.vanity_url == "" or self.vanity_url is None:
            vanity = "No Vanity URL set"
        else:
            vanity = self.vanity_url
        return f"{base} - {vanity}"

class DjangoContentType(ContentType):
    pass
