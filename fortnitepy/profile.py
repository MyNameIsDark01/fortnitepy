from datetime import timedelta, datetime, timezone
from typing import Optional, List, Dict

from .enums import CosmeticType, VBucksPlatform, SaveTheWorldFounderPack
from .utils import from_iso


class BattleRoyaleProfile:

    def __init__(self, data: dict):
        self.items = [ItemProfile(item) for item in data['items'].values()]

        stats = data['stats']['attributes']

        self.account_level: int = stats['accountLevel']

        self.season: int = stats['season_num']
        self.season_level: int = stats['level']
        self.season_levels_purchased: int = stats.get('season_levels_purchased', 0)
        season_stats = stats.get('season') or {}
        self.season_wins: int = season_stats.get('numWins', 0)
        self.last_match_ended_at: Optional[datetime] = \
            from_iso(stats['last_match_end_datetime']) if 'last_match_end_datetime' in stats else None

        self.total_season_battlestars: int = stats.get('battlestars_season_total', 0)
        self.battle_stars: int = stats.get('battlestars', 0)
        self.purchased_battlepass_offers: List[PurchasedBattlePassOffer] = [
            PurchasedBattlePassOffer(offer) for offer in stats.get('purchased_bp_offers', [])
        ]

        self.total_season_style_points: int = stats.get('style_points_season_total', 0)
        self.style_points: int = stats.get('style_points', 0)

        self.lifetime_wins: int = stats.get('lifetime_wins', 0)
        self.past_season_stats: List[PastSeasonStats] = [
            PastSeasonStats(ss) for ss in stats.get('past_seasons', [])
        ]

        self.saved_loadout_ids: List[str] = stats['loadouts']
        self.use_random_loadout = stats.get('use_random_loadout', False)
        self.last_applied_loadout_id: Optional[str] = stats.get('last_applied_loadout')

        self.season_match_boost: int = stats.get('season_match_boost', 0)
        self.season_friend_match_boost: int = stats.get('season_friend_match_boost', 0)

        self.has_claimed_2fa_reward: bool = stats.get('mfa_reward_claimed', False)
        self.has_ranked_access = bool = stats.get('habanero_unlocked', False)

        self.party_assist_quest: Optional[str] = stats.get('party_assist_quest')

        self.xp = stats.get('xp', 0)
        self.last_xp_interaction: Optional[datetime] = \
            from_iso(stats['last_xp_interaction']) if 'last_xp_interaction' in stats else None
        self.supercharged_xp: int = stats.get('rested_xp', 0)
        self.supercharged_xp_multiplier: Optional[float] = stats.get('rested_xp_mult')
        self.supercharged_xp_overflow: int = stats.get('rested_xp_overflow', 0)
        self.supercharged_xp_exchange: Optional[float] = stats.get('rested_xp_exchange')
        self.supercharged_xp_golden_path_granted: int = stats.get('rested_xp_golden_path_granted', 0)
        self.supercharged_xp_cumulative: int = stats.get('rested_xp_cumulative', 0)
        self.supercharged_xp_consumed_cumulative: int = stats.get('rested_xp_consumed_cumulative', 0)

        self.has_purchased_battlepass: bool = stats.get('book_purchased', False)
        self.battlepass_level: int = stats['book_level']
        self.battlepass_xp: Optional[int] = stats.get('book_xp')

        self.creative_dynamic_xp: Optional[dict] = stats.get('creative_dynamic_xp')
        self.vote_data: Optional[dict] = stats.get('vote_data')

        self.raw_data = data

    def get_cosmetics(self, *cosmetic_types: CosmeticType) -> List["ItemProfile"]:
        if not cosmetic_types:
            cosmetic_types = list(CosmeticType)
        cosmetic_types = [cosmetic_type.value for cosmetic_type in cosmetic_types]
        return [i for i in self.items if i.type in cosmetic_types]

    def get_legacies(self) -> List["ItemProfile"]:
        return [item for item in self.items if item.type == 'Accolades']

    def get_locker(self) -> "Locker":
        item = [item for item in self.items if item.type == 'CosmeticLocker'][0]
        return Locker(item.attributes)

    def get_victory_crown_overview(self) -> Optional["VictoryCrownOverview"]:
        items = [item for item in self.items if item.type == 'VictoryCrown' and item.id == 'defaultvictorycrown']
        if not items:
            return None
        item = items[0]
        if 'victory_crown_account_data' not in item.attributes:
            return None
        return VictoryCrownOverview(item.attributes['victory_crown_account_data'])


class VictoryCrownOverview:

    def __init__(self, data: dict):
        self.has_crown: bool = data['has_victory_crown']
        self.crowns_bestowed: int = data['total_victory_crowns_bestowed_count']
        self.crown_wins: int = data['total_royal_royales_achieved_count']


class PastSeasonStats:

    def __init__(self, data: dict):
        self.season: int = data['seasonNumber']
        self.wins: int = data['numWins']
        self.xp: int = data['seasonXp']
        self.level: int = data['seasonLevel']
        self.battlepass_xp: int = data['bookXp']
        self.battlepass_level: int = data['bookLevel']
        self.has_purchased_battle_pass: bool = data['purchasedVIP']
        self.crown_wins: int = data['numRoyalRoyales']

        self.raw_data: dict = data


class PurchasedBattlePassOffer:

    def __init__(self, data: dict):
        self.offer_id: str = data['offerId']
        self.free_reward: bool = data['bIsFreePassReward']
        self.purchase_date: datetime = from_iso(data['purchaseDate'])
        self.items = [
            Item(item) for item in data['lootResult']
        ]
        self.currency: str = data['currencyType']
        self.currency_paid: int = data['totalCurrencyPaid']

        self.attributes: Optional[dict] = data.get('attributes')

        self.raw_data: dict = data


class Item:

    def __init__(self, data: dict):
        item_type_split = data['itemType'].split(':')
        self.type: str = item_type_split[0]
        self.id: str = item_type_split[1]
        self.guid: Optional[str] = data.get('itemGuid')
        self.profile: Optional[str] = data.get('itemProfile')
        self.quantity: int = data['quantity']


class ItemProfile:

    def __init__(self, data: dict):
        self.template_id: str = data['templateId']
        item_type_split = self.template_id.split(':')
        self.type: str = item_type_split[0]
        self.id: str = item_type_split[1]
        self.attributes: dict = data['attributes']
        self.quantity: int = data['quantity']


class Locker:

    def __init__(self, data: dict):
        self.outfit: LockerSlot = LockerSlot(data['locker_slots_data']['slots']['Character'])
        self.backpack: LockerSlot = LockerSlot(data['locker_slots_data']['slots']['Backpack'])
        self.harvesting_tool: LockerSlot = LockerSlot(data['locker_slots_data']['slots']['Pickaxe'])
        self.glider: LockerSlot = LockerSlot(data['locker_slots_data']['slots']['Glider'])
        self.contrail: LockerSlot = LockerSlot(data['locker_slots_data']['slots']['SkyDiveContrail'])
        self.emote: LockerSlot = LockerSlot(data['locker_slots_data']['slots']['Dance'])
        self.music: LockerSlot = LockerSlot(data['locker_slots_data']['slots']['MusicPack'])
        self.wrap: LockerSlot = LockerSlot(data['locker_slots_data']['slots']['ItemWrap'])
        self.loading_screen: LockerSlot = LockerSlot(data['locker_slots_data']['slots']['LoadingScreen'])
        self.name: Optional[str] = data.get('locker_name')
        self.banner_icon_id: Optional[str] = data.get('banner_icon_template')
        self.banner_color_id: Optional[str] = data.get('banner_color_template')
        self.use_count: Optional[int] = data.get('useCount')


class LockerSlot:

    def __init__(self, data: dict):
        self.name: Optional[str] = data.get('locker_slot_name')
        self.use_count: int = data['useCount']
        self.item: Optional[ItemProfile] = data.get('item')


class CommonCoreProfile:

    def __init__(self, data: dict):
        self.items = [ItemProfile(item) for item in data['items'].values()]
        stats = data['stats']['attributes']

        self.promotion_status: Optional[PromotionStatus] = PromotionStatus(stats['promotion']) \
            if 'promotion' in stats else None
        self.survey_data: Optional[dict] = stats.get('survey_data')
        self.intro_game_played: bool = stats.get('intro_game_played', False)
        self.vbucks_purchase_history: Optional[VBucksPurchaseHistory] \
            = VBucksPurchaseHistory(stats['mtx_purchase_history']) if 'mtx_purchase_history' in stats else None
        self.money_purchase_history: Optional[MoneyPurchaseHistory] \
            = MoneyPurchaseHistory(stats['rmt_purchase_history']) if 'rmt_purchase_history' in stats else None
        self.gift_history: Optional[GiftHistory] = GiftHistory(stats['gift_history']) \
            if 'gift_history' in stats else None

        self.undo_cooldowns: List[UndoCooldown] = [
            UndoCooldown(cooldown) for cooldown in stats.get('undo_cooldowns', [])
        ]

        self.creator_code: Optional[str] = stats.get('mtx_affiliate')
        self.creator_code_owner_id: Optional[str] = stats.get('mtx_affiliate_id')
        self.creator_code_set_on: Optional[datetime] = from_iso(stats['mtx_affiliate_set_time']) \
            if 'mtx_affiliate_set_time' in stats else None

        self.current_vbucks_platform: VBucksPlatform = VBucksPlatform(stats['current_mtx_platform'])
        in_app_purchases = stats.get('in_app_purchases', {})
        self.receipt_ids: List[str] = in_app_purchases.get('receipts', [])

        self.allowed_sending_gifts: bool = stats['allowed_to_send_gifts']
        self.allowed_receiving_gifts: bool = stats['allowed_to_receive_gifts']

        self.enabled_2fa = stats.get('mfa_enabled', False)

        self.ban_status: Optional[BanStatus] = BanStatus(stats['ban_status']) if 'ban_status' in stats else None
        self.ban_history: Optional[BanHistory] = BanHistory(stats['ban_history']) \
            if 'ban_history' in stats else None

        self.raw_data: dict = data

    @property
    def has_custom_games_access(self):
        return any(item.id == 'athenacancreatecustomgames_token' for item in self.items)

    @property
    def has_save_the_world_access(self):
        return any(item.id == 'campaignaccess' for item in self.items)

    @property
    def save_the_world_founder_pack(self) -> Optional[SaveTheWorldFounderPack]:
        if owned_founder_packs := [
            int(item.id.split('_')[1])
            for item in self.items
            if item.type == 'Token' and item.id.startswith('founderspack_')
        ]:
            return SaveTheWorldFounderPack(max(owned_founder_packs))
        else:
            return None

    @property
    def has_valid_creator_code(self) -> bool:
        return (
            (self.creator_code or self.creator_code_owner_id)
            and self.creator_code_set_on
            and (datetime.now(timezone.utc) - self.creator_code_set_on).days < 14
        )

    def get_overall_vbucks_count(self, platform: Optional[VBucksPlatform] = None, strict: bool = False) -> int:
        return sum((
            self.get_save_the_world_vbucks(),
            self.get_purchased_vbucks(platform, strict),
            self.get_free_obtained_vbucks()
        )) - self.get_vbucks_debt()

    def get_save_the_world_vbucks(self) -> int:
        return sum(item.quantity for item in self.items if item.type == 'Currency' and item.id == 'MtxComplimentary')

    def get_purchased_vbucks(self, platform: Optional[VBucksPlatform] = None, strict: bool = False) -> int:
        platforms = {platform}
        if not strict:
            if platform is not VBucksPlatform.NINTENDO:
                platforms = set(VBucksPlatform) - {VBucksPlatform.NINTENDO}
            else:
                platforms = {VBucksPlatform.NINTENDO}
        platforms = [platform.value for platform in platforms]

        return sum(
            item.quantity for item in self.items
            if (
                    item.type == 'Currency' and item.id == 'MtxPurchased' or
                    item.type == 'Currency' and item.id == 'MtxPurchaseBonus'
            ) and (
                    platform is None or item.attributes['platform'] in platforms
            )
        )

    def get_free_obtained_vbucks(self) -> int:
        return sum(item.quantity for item in self.items if item.id == 'MtxGiveaway')

    def get_vbucks_debt(self) -> int:
        return sum(item.quantity for item in self.items if item.id == 'MtxDebt')

    def get_banner(self) -> List[ItemProfile]:
        return [item for item in self.items if item.type == 'HomebaseBannerIcon']

    def get_banner_color(self):
        return [item for item in self.items if item.type == 'HomebaseBannerColor']


class PromotionStatus:

    def __init__(self, data: dict):
        self.name: str = data['promoName']
        self.eligible: bool = data['eligible']
        self.redeemed: bool = data['redeemed']
        self.notified: bool = data['notified']


class VBucksPurchaseHistory:

    def __init__(self, data: dict):
        self.refunds_used: int = data['refundsUsed']
        self.refund_credits: int = data['refundCredits']
        self.next_refund_grant_at: Optional[datetime] = (
                from_iso(data['tokenRefreshReferenceTime']) + timedelta(days=365)
        ) if data.get('tokenRefreshReferenceTime') else None
        self.purchases: List[VBucksPurchase] = [VBucksPurchase(purchase) for purchase in data['purchases']]


class MoneyPurchaseHistory:

    def __init__(self, data: dict):
        self.purchases: List[MoneyPurchase] = [MoneyPurchase(purchase) for purchase in data['purchases']]


class GiftUser:

    def __init__(self, user_id: str, timestamp: str):
        self.user_id: str = user_id
        self.timestamp: datetime = from_iso(timestamp)


class Gift:

    def __init__(self, data: dict):
        self.sent_at: datetime = from_iso(data['date'])
        self.offer_id: str = data['offerId']
        self.recipient_user_id: str = data['toAccountId']


class GiftHistory:

    def __init__(self, data: dict):
        self.sent_count: int = data['num_sent']
        self.received_count: int = data['num_received']
        self.sent_to: List[GiftUser] = [GiftUser(uid, ts) for uid, ts in data['sentTo'].items()]
        self.received_from: List[GiftUser] = [GiftUser(uid, ts) for uid, ts in data['receivedFrom'].items()]
        self.gifts: List[Gift] = [Gift(gift) for gift in data['gifts']]

    @property
    def daily_remaining(self) -> int:
        return 5 - len(
            [
                g
                for g in self.gifts
                if g.sent_at > datetime.now(timezone.utc) - timedelta(days=1)
            ]
        )


class VBucksPurchase:
    def __init__(self, data: dict):
        self.id: str = data['purchaseId']
        self.offer_id: str = data['offerId']
        self.purchased_at: datetime = from_iso(data['purchaseDate'])
        self.undoable_until: Optional[datetime] = from_iso(data['undoTimeout']) if 'undoTimeout' in data else None
        self.refunded_at: Optional[datetime] = from_iso(data['refundDate']) if 'refundDate' in data else None
        self.free_refund_eligible: bool = data.get('freeRefundEligible', False)
        self.fulfillments: list = data['fulfillments']
        self.price: int = data['totalMtxPaid']
        metadata = data.get('metadata', {})
        self.creator_code: Optional[str] = metadata.get('mtx_affiliate')
        self.creator_code_owner_id: Optional[str] = metadata.get('mtx_affiliate_id')
        self.game_context: Optional[str] = data.get('gameContext')
        self.items: List[Item] = [Item(item) for item in data['lootResult']]


class MoneyPurchase:
    def __init__(self, data: dict):
        self.fulfillment_id: str = data['fulfillmentId']
        self.purchased_at: datetime = from_iso(data['purchaseDate'])
        self.items: List[Item] = [Item(item) for item in data['lootResult']]


class UndoCooldown:

    def __init__(self, data: dict):
        self.offer_id: str = data['offerId']
        self.expires_at: datetime = from_iso(data['cooldownExpires'])


class BanStatus:

    def __init__(self, data: dict):
        self.required_user_acknowledgement: bool = data['bRequiresUserAck']
        self.reasons: List[str] = data['banReasons']
        self.has_started: bool = data['bBanHasStarted']
        self.started_at: datetime = from_iso(data['banStartTimeUtc'])
        self.duration_days: int = data['banDurationDays']
        self.exploit_program_name: Optional[str] = data.get('exploitProgramName')
        self.additional_info: Optional[str] = data.get('additionalInfo')
        self.competitive_ban_reason: str = data.get('competitiveBanReason')


class BanHistory:

    def __init__(self, data: dict):
        self.ban_count: Dict[str, int] = data['banCount']
        self.ban_tier: Dict[str, int] = data['banTier']


class SaveTheWorldProfile:

    def __init__(self, data: dict):
        self.items = [ItemProfile(item) for item in data['items'].values()]

        stats = data['stats']['attributes']

        self.xp: int = stats.get('xp', 0)
        self.level: int = stats['level']

        self.mfa_reward_claimed: bool = stats.get('mfa_reward_claimed', False)

        self.daily_rewards: Optional[DailyRewards] = DailyRewards(stats['daily_rewards']) \
            if 'daily_rewards' in stats else None

        self.raw_data = data

    def get_cosmetics(self, *cosmetic_types: CosmeticType) -> List["ItemProfile"]:
        if not cosmetic_types:
            cosmetic_types = list(CosmeticType)
        cosmetic_types = [cosmetic_type.value for cosmetic_type in cosmetic_types]
        return [i for i in self.items if i.type in cosmetic_types]

    def get_legacies(self) -> List["ItemProfile"]:
        return [item for item in self.items if item.type == 'Accolades']

    def get_locker(self) -> "Locker":
        item = [item for item in self.items if item.type == 'CosmeticLocker'][0]
        return Locker(item.attributes)


class DailyRewards:

    def __init__(self, data: dict):
        self.next_default_reward: int = data['nextDefaultReward']
        self.total_days_logged_in: int = data['totalDaysLoggedIn']
        self.last_claimed_at: datetime = from_iso(data['lastClaimDate'])


class DailyRewardNotification:

    def __init__(self, data: dict):
        self.days_logged_in: int = data['daysLoggedIn']
        self.items: List[NotificationItem] = [NotificationItem(reward) for reward in data['items']]


class NotificationItem:

    def __init__(self, data: dict):
        self.type: str = data['itemType']
        item_type_split = self.type.split(':')
        self.type: str = item_type_split[0]
        self.id: str = item_type_split[1]
        self.guid: str = data['itemGuid']
        self.profile: str = data['itemProfile']
        self.quantity: int = data['quantity']


class BattleRoyaleInventory:

    def __init__(self, data: dict):
        self.global_gold: int = data['stash']['globalcash']
