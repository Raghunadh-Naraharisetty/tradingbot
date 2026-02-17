"""
NEWS_INTEGRATION.PY — Free News & Sentiment Engine
===================================================
Three free data sources:

  1. ALPACA NEWS API  — Financial news (already have API key!)
     • Real-time news from Reuters, Benzinga, etc.
     • Sentiment: positive/negative/neutral per article
     • Completely FREE with Alpaca account

  2. REDDIT SENTIMENT — r/wallstreetbets, r/stocks
     • Stock mentions count (hype indicator)
     • Positive/negative sentiment
     • FREE via PRAW (no key needed for read-only)

  3. EARNINGS CALENDAR — Yahoo Finance
     • When is next earnings date for each stock?
     • Bot pauses trading 2 days before earnings
     • Prevents huge unexpected losses
     • FREE

Usage:
    from news_integration import NewsIntegration
    news = NewsIntegration(alpaca_api)
    context = news.get_full_context("AAPL")
"""

import os
from datetime import datetime, timedelta
import pytz


class NewsIntegration:
    """Unified news + sentiment + calendar integration."""

    def __init__(self, alpaca_api=None):
        self.alpaca = alpaca_api
        self._reddit = None
        self._reddit_attempted = False

    # ─────────────────────────────────────────────────────────
    # 1. ALPACA NEWS (FREE — already have API!)
    # ─────────────────────────────────────────────────────────

    def get_alpaca_news(self, symbol: str, limit: int = 10) -> dict:
        """
        Fetch recent news from Alpaca News API.
        Returns sentiment score and top headlines.
        """
        if not self.alpaca:
            return self._empty_news("Alpaca not connected")

        try:
            end   = datetime.now(pytz.utc)
            start = end - timedelta(days=3)

            news_items = self.alpaca.get_news(
                symbol,
                start=start.isoformat(),
                end=end.isoformat(),
                limit=limit
            )

            if not news_items:
                return self._empty_news("No recent news")

            headlines   = []
            pos_count   = 0
            neg_count   = 0
            neu_count   = 0

            # Positive and negative keywords
            POS_WORDS = {
                "surge", "soar", "beat", "record", "strong", "growth",
                "profit", "gain", "rise", "up", "bullish", "upgrade",
                "buy", "outperform", "revenue", "success", "launch",
                "partnership", "deal", "award", "innovation", "expansion"
            }
            NEG_WORDS = {
                "fall", "drop", "miss", "weak", "loss", "decline",
                "down", "bearish", "downgrade", "sell", "underperform",
                "lawsuit", "probe", "fine", "recall", "cut", "layoff",
                "disappoints", "concern", "risk", "warning", "crisis"
            }

            for item in news_items:
                headline = item.headline if hasattr(item, 'headline') else str(item)
                headline_lower = headline.lower()

                # Score each headline
                pos = sum(1 for w in POS_WORDS if w in headline_lower)
                neg = sum(1 for w in NEG_WORDS if w in headline_lower)

                if pos > neg:
                    sentiment = "POSITIVE"
                    pos_count += 1
                elif neg > pos:
                    sentiment = "NEGATIVE"
                    neg_count += 1
                else:
                    sentiment = "NEUTRAL"
                    neu_count += 1

                headlines.append({
                    "headline":  headline[:120],
                    "sentiment": sentiment,
                    "url":       item.url if hasattr(item, 'url') else "",
                    "published": str(item.created_at)[:10] if hasattr(item, 'created_at') else "",
                })

            total = len(headlines)
            if total == 0:
                overall = "NEUTRAL"
                score   = 0
            else:
                score = (pos_count - neg_count) / total * 10
                if score > 2:
                    overall = "POSITIVE"
                elif score < -2:
                    overall = "NEGATIVE"
                else:
                    overall = "NEUTRAL"

            return {
                "available":   True,
                "source":      "Alpaca News",
                "symbol":      symbol,
                "overall":     overall,
                "score":       round(score, 1),
                "pos_count":   pos_count,
                "neg_count":   neg_count,
                "neu_count":   neu_count,
                "total":       total,
                "headlines":   headlines[:5],
                "signal_boost": self._news_to_boost(overall),
            }

        except Exception as e:
            return self._empty_news(f"Error: {str(e)[:60]}")

    # ─────────────────────────────────────────────────────────
    # 2. REDDIT SENTIMENT (FREE)
    # ─────────────────────────────────────────────────────────

    def _init_reddit(self):
        """Initialize Reddit client (read-only, no auth needed)."""
        if self._reddit_attempted:
            return self._reddit
        self._reddit_attempted = True
        try:
            import praw
            self._reddit = praw.Reddit(
                client_id="AlphaSignalBot",
                client_secret="",
                user_agent="AlphaSignalBot/1.0 (by u/trading_bot)"
            )
        except ImportError:
            self._reddit = None
        except Exception:
            self._reddit = None
        return self._reddit

    def get_reddit_sentiment(self, symbol: str) -> dict:
        """
        Get Reddit mention count and sentiment for a symbol.
        Searches r/wallstreetbets, r/stocks, r/investing.
        """
        try:
            reddit = self._init_reddit()
            if not reddit:
                return self._empty_reddit("praw not installed")

            subreddits = ["wallstreetbets", "stocks", "investing"]
            mentions   = 0
            pos_count  = 0
            neg_count  = 0
            top_posts  = []

            POS_WORDS = {"bull", "buy", "moon", "calls", "long", "bullish",
                         "up", "green", "gain", "profit", "love", "great"}
            NEG_WORDS = {"bear", "sell", "puts", "short", "bearish",
                         "down", "red", "loss", "crash", "hate", "worst"}

            for sub_name in subreddits:
                try:
                    sub = reddit.subreddit(sub_name)
                    results = list(sub.search(
                        f"${symbol} OR \"{symbol}\"",
                        time_filter="day",
                        limit=15
                    ))

                    for post in results:
                        mentions += 1
                        text = (post.title + " " + (post.selftext or "")).lower()
                        pos = sum(1 for w in POS_WORDS if w in text)
                        neg = sum(1 for w in NEG_WORDS if w in text)
                        if pos > neg:   pos_count += 1
                        elif neg > pos: neg_count += 1
                        if len(top_posts) < 3:
                            top_posts.append({
                                "title":     post.title[:100],
                                "score":     post.score,
                                "subreddit": sub_name,
                                "upvotes":   post.score,
                            })
                except Exception:
                    continue

            if mentions == 0:
                overall = "NEUTRAL"
                score   = 0
            else:
                score = (pos_count - neg_count) / mentions * 10
                if score > 2:   overall = "POSITIVE"
                elif score < -2: overall = "NEGATIVE"
                else:            overall = "NEUTRAL"

            # Hype level: more mentions = more attention
            if mentions >= 30:   hype = "🔥 VIRAL"
            elif mentions >= 15: hype = "📈 HIGH"
            elif mentions >= 5:  hype = "📊 MODERATE"
            else:                hype = "🔇 LOW"

            return {
                "available":    True,
                "source":       "Reddit",
                "symbol":       symbol,
                "overall":      overall,
                "score":        round(score, 1),
                "mentions":     mentions,
                "pos_count":    pos_count,
                "neg_count":    neg_count,
                "hype":         hype,
                "top_posts":    top_posts,
                "signal_boost": self._news_to_boost(overall),
            }

        except Exception as e:
            return self._empty_reddit(str(e)[:60])

    # ─────────────────────────────────────────────────────────
    # 3. EARNINGS CALENDAR (FREE via yfinance)
    # ─────────────────────────────────────────────────────────

    def get_earnings_info(self, symbol: str) -> dict:
        """
        Check next earnings date.
        Returns warning if earnings within 2 days.
        """
        try:
            import yfinance as yf
            ticker   = yf.Ticker(symbol)
            calendar = ticker.calendar

            if calendar is None or calendar.empty:
                return {"available": False, "warning": False, "message": "No earnings data"}

            # Get next earnings date
            if "Earnings Date" in calendar.index:
                earnings_dates = calendar.loc["Earnings Date"]
                if hasattr(earnings_dates, '__iter__'):
                    next_earnings = earnings_dates.iloc[0] if len(earnings_dates) > 0 else None
                else:
                    next_earnings = earnings_dates
            else:
                return {"available": False, "warning": False, "message": "No earnings date"}

            if next_earnings is None:
                return {"available": False, "warning": False, "message": "No earnings date"}

            # Convert to datetime
            import pandas as pd
            if not isinstance(next_earnings, pd.Timestamp):
                next_earnings = pd.Timestamp(next_earnings)

            now          = pd.Timestamp.now(tz=next_earnings.tz)
            days_until   = (next_earnings - now).days

            if days_until <= 0:
                warning = True
                message = "⚠️ EARNINGS TODAY — Skip trading!"
                severity = "CRITICAL"
            elif days_until <= 1:
                warning = True
                message = "⚠️ Earnings TOMORROW — High risk!"
                severity = "HIGH"
            elif days_until <= 2:
                warning = True
                message = f"⚠️ Earnings in {days_until} days — Use caution"
                severity = "MEDIUM"
            else:
                warning = False
                message = f"✅ Next earnings: {next_earnings.strftime('%d %b %Y')} ({days_until}d away)"
                severity = "NONE"

            return {
                "available":   True,
                "warning":     warning,
                "severity":    severity,
                "message":     message,
                "days_until":  days_until,
                "date":        next_earnings.strftime("%d %b %Y"),
            }

        except Exception as e:
            return {"available": False, "warning": False, "message": f"Calendar error: {str(e)[:40]}"}

    # ─────────────────────────────────────────────────────────
    # COMBINED CONTEXT
    # ─────────────────────────────────────────────────────────

    def get_full_context(self, symbol: str) -> dict:
        """
        Get all news/sentiment/calendar data for one symbol.
        This is the main function to call from the scheduler.
        """
        alpaca_news = self.get_alpaca_news(symbol)
        earnings    = self.get_earnings_info(symbol)

        # Reddit is slow — only fetch if Alpaca news is neutral
        if alpaca_news["overall"] == "NEUTRAL":
            reddit = self.get_reddit_sentiment(symbol)
        else:
            reddit = self._empty_reddit("Skipped (Alpaca news sufficient)")

        # Combined sentiment
        sentiments = [
            alpaca_news["overall"],
            reddit["overall"] if reddit["available"] else "NEUTRAL"
        ]
        pos = sentiments.count("POSITIVE")
        neg = sentiments.count("NEGATIVE")
        if pos > neg:   combined = "POSITIVE"
        elif neg > pos: combined = "NEGATIVE"
        else:           combined = "NEUTRAL"

        # Net signal boost/reduction
        total_boost = (
            alpaca_news.get("signal_boost", 0) +
            reddit.get("signal_boost", 0)
        )

        return {
            "symbol":       symbol,
            "alpaca_news":  alpaca_news,
            "reddit":       reddit,
            "earnings":     earnings,
            "combined":     combined,
            "total_boost":  total_boost,
            "should_skip":  earnings["warning"] and earnings.get("severity") in ("CRITICAL", "HIGH"),
            "skip_reason":  earnings["message"] if earnings["warning"] else None,
        }

    def apply_news_to_signal(self, signal: str, confidence: str,
                              score: float, context: dict) -> tuple:
        """
        Adjust signal confidence based on news context.

        Returns updated (signal, confidence, score, note)
        """
        if context["should_skip"]:
            return "HOLD", "HOLD", 0, f"BLOCKED: {context['skip_reason']}"

        boost = context["total_boost"]
        news_overall = context["combined"]

        # News confirms signal
        if signal == "BUY" and news_overall == "POSITIVE":
            boost += 1.5
            note = "📰 News confirms BUY signal"
        elif signal == "SELL" and news_overall == "NEGATIVE":
            boost += 1.5
            note = "📰 News confirms SELL signal"
        # News contradicts signal
        elif signal == "BUY" and news_overall == "NEGATIVE":
            boost -= 2.0
            note = "⚠️ News contradicts BUY — reducing confidence"
        elif signal == "SELL" and news_overall == "POSITIVE":
            boost -= 2.0
            note = "⚠️ News contradicts SELL — reducing confidence"
        else:
            note = "📰 News: neutral"

        new_score = min(10, max(0, score + boost))

        # Re-evaluate confidence
        if new_score >= 7:    new_conf = "STRONG"
        elif new_score >= 4.5: new_conf = "MEDIUM"
        elif new_score >= 2:   new_conf = "WEAK"
        else:
            # Score too low after news penalty → skip
            return "HOLD", "HOLD", new_score, f"Downgraded: {note}"

        return signal, new_conf, new_score, note

    # ─────────────────────────────────────────────────────────
    # HELPERS
    # ─────────────────────────────────────────────────────────

    def _news_to_boost(self, overall: str) -> float:
        return {"POSITIVE": 1.0, "NEUTRAL": 0.0, "NEGATIVE": -1.0}.get(overall, 0.0)

    def _empty_news(self, reason: str) -> dict:
        return {
            "available": False, "source": "Alpaca News",
            "overall": "NEUTRAL", "score": 0,
            "pos_count": 0, "neg_count": 0, "total": 0,
            "headlines": [], "signal_boost": 0, "message": reason,
        }

    def _empty_reddit(self, reason: str) -> dict:
        return {
            "available": False, "source": "Reddit",
            "overall": "NEUTRAL", "score": 0,
            "mentions": 0, "pos_count": 0, "neg_count": 0,
            "hype": "—", "top_posts": [], "signal_boost": 0, "message": reason,
        }
