from django.contrib.auth.models import User
from django.db import models
from django.db.models import signals
from django.template.defaultfilters import slugify
from stream_django import activity
from stream_django.feed_manager import feed_manager


class Tweet(activity.Activity, models.Model):

    user = models.ForeignKey('auth.User')
    text = models.CharField(max_length=160)

    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def print_self(self):
        print(self.text)

    @property
    def activity_object_attr(self):
        return self

    def save(self):
        self.create_hashtags()
        super(Tweet, self).save()

    def create_hashtags(self):
        hashtag_set = set(self.parse_hashtags())
        for hashtag in hashtag_set:
            # TODO: increment counters in one query
            # Hashtag.objects.filter(or_conditions).update((F('used_amount')+1))
            h, created = Hashtag.objects.get_or_create(name=hashtag)
            h.occurrences += 1
            h.save()

    def parse_hashtags(self):
        return [slugify(i) for i in self.text.split() if i.startswith("#")]

    def parse_mentions(self):
        mentions = [slugify(i) for i in self.text.split() if i.startswith("@")]
        return User.objects.filter(username__in=mentions)

    def parse_all(self):
        parts = self.text.split()
        hashtag_counter = 0
        mention_counter = 0
        result = {u"parsed_text": u"", u"hashtags": [], u"mentions": []}
        for index, value in enumerate(parts):
            if value.startswith("#"):
                parts[index] = u"{hashtag" + str(hashtag_counter) + u"}"
                hashtag_counter += 1
                result[u'hashtags'].append(value)
            if value.startswith("@"):
                parts[index] = u"{mention" + str(mention_counter) + u"}"
                mention_counter += 1
                result[u'mentions'].append(value)
        result[u'parsed_text'] = " ".join(parts)
        return result

    @property
    def activity_notify(self):
        targets = []
        for hashtag in self.parse_hashtags():
            targets.append(feed_manager.get_feed('hashtag', hashtag))
        for user in self.parse_mentions():
            targets.append(feed_manager.get_news_feeds(user.id)['flat'])
        return targets


class Follow(models.Model):
    user = models.ForeignKey('auth.User', related_name='friends')
    target = models.ForeignKey('auth.User', related_name='followers')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'target')


class UserProfile(models.Model):
    user = models.OneToOneField(User)
    description = models.TextField()
    picture = models.ImageField(upload_to='profile_pictures', blank=True)


class Hashtag(models.Model):
    name = models.CharField(max_length=160)
    occurrences = models.IntegerField(default=0)


def unfollow_feed(sender, instance, **kwargs):
    feed_manager.unfollow_user(instance.user_id, instance.target_id)


def follow_feed(sender, instance, created, **kwargs):
    if created:
        feed_manager.follow_user(instance.user_id, instance.target_id)


signals.post_delete.connect(unfollow_feed, sender=Follow)
signals.post_save.connect(follow_feed, sender=Follow)
