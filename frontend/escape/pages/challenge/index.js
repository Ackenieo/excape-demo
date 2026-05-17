const {
  palette,
  drawRoundedRect,
  drawCircularAvatar,
  isPointInRect,
  drawTabBar,
} = require('../../core/ui');

function createChallengeScene(app) {
  const tabs = [
    { x: 0, y: 0, width: 0, height: 60, action: 'home' },
    { x: 0, y: 0, width: 0, height: 60, action: 'rank' },
    { x: 0, y: 0, width: 0, height: 60, action: 'profile' }
  ];
  const avatarTapRect = { x: 0, y: 0, width: 0, height: 0 };
  const avatarActionRect = { x: 0, y: 0, width: 0, height: 0 };

  function getProfileData() {
    const profile = app.appStore.profile || {};
    const rankings = app.appStore.rankings || {};
    const stats = rankings.stats || {};
    const overall = Array.isArray(rankings.overall) ? rankings.overall : [];
    const topPlayer = overall[0] || null;

    const nickname = profile.nickname
      || (topPlayer && topPlayer.nickname)
      || '匿名玩家';
    const passedCount = typeof profile.passedCount === 'number'
      ? profile.passedCount
      : Math.max(0, Math.round((stats.playCount || 0) * (parseFloat(stats.passRate) || 0) / 100));
    const totalScore = typeof profile.totalScore === 'number'
      ? profile.totalScore
      : (typeof stats.bestScore === 'number' ? stats.bestScore : 0);
    const passRate = profile.passRate || stats.passRate || '0%';
    const rankText = profile.rankText || (topPlayer ? '排行榜实时数据' : '等待后端数据');
    const title = '个人中心';
    const avatarUrl = profile.avatarUrl || app.getUserAvatarSource();
    const achievements = Array.isArray(profile.achievements) && profile.achievements.length
      ? profile.achievements.slice(0, 4)
      : [
        { title: '初出茅庐', desc: '等待后端返回', active: false },
        { title: '一针见血', desc: '等待后端返回', active: false },
        { title: 'AI 克星', desc: '等待后端返回', active: false },
        { title: '越狱大师', desc: '等待后端返回', active: false },
      ];
    const recentRuns = Array.isArray(profile.recentRuns) && profile.recentRuns.length
      ? profile.recentRuns.slice(0, 3)
      : overall.slice(0, 3).map((item, index) => ({
        name: `${item.nickname || '匿名玩家'} · 关卡 ${item.levelId || '--'}`,
        score: `${item.score || 0}`,
        color: index === 0 ? palette.warning : palette.success,
      }));

    return {
      nickname,
      rankText,
      passedCount,
      totalScore,
      passRate,
      title,
      avatarUrl,
      achievements,
      recentRuns,
    };
  }

  return {
    render({ ctx, width, height }) {
      const profile = getProfileData();
      ctx.fillStyle = palette.bgSecondary;
      ctx.fillRect(0, 0, width, height);

      // Hero
      ctx.fillStyle = palette.bg;
      ctx.fillRect(0, 0, width, 180);

      const cx = width / 2;
      avatarTapRect.x = cx - 34;
      avatarTapRect.y = 28;
      avatarTapRect.width = 68;
      avatarTapRect.height = 68;
      const avatarImage = app.getImageAsset(profile.avatarUrl);
      drawCircularAvatar(ctx, avatarImage, cx - 26, 34, 52, {
        fallbackText: (profile.nickname || '我').slice(0, 1),
        fallbackFill: palette.primaryLight,
        textColor: palette.primaryText,
      });

      ctx.fillStyle = palette.primaryText;
      ctx.font = 'bold 16px sans-serif';
      ctx.textAlign = 'center';
      ctx.fillText(profile.nickname, cx, 110);

      ctx.fillStyle = palette.textSub;
      ctx.font = '10px sans-serif';
      ctx.fillText(profile.rankText || profile.title, cx, 125);

      avatarActionRect.x = cx - 48;
      avatarActionRect.y = 136;
      avatarActionRect.width = 96;
      avatarActionRect.height = 26;
      drawRoundedRect(
        ctx,
        avatarActionRect.x,
        avatarActionRect.y,
        avatarActionRect.width,
        avatarActionRect.height,
        13,
        palette.bgSecondary,
        palette.border,
      );
      ctx.fillStyle = palette.primary;
      ctx.font = '11px sans-serif';
      ctx.textAlign = 'center';
      ctx.textBaseline = 'middle';
      ctx.fillText('更换头像', cx, avatarActionRect.y + avatarActionRect.height / 2);
      ctx.textBaseline = 'alphabetic';

      // Stats
      ctx.beginPath();
      ctx.moveTo(20, 176); ctx.lineTo(width - 20, 176);
      ctx.strokeStyle = palette.borderLight; ctx.stroke();

      const statW = width / 3;
      ctx.fillStyle = palette.textMain; ctx.font = 'bold 16px sans-serif';
      ctx.fillText(String(profile.passedCount), statW * 0.5, 196);
      ctx.fillText(String(profile.totalScore), statW * 1.5, 196);
      ctx.fillText(profile.passRate, statW * 2.5, 196);

      ctx.fillStyle = palette.textSub; ctx.font = '10px sans-serif';
      ctx.fillText('已通关', statW * 0.5, 211);
      ctx.fillText('总分', statW * 1.5, 211);
      ctx.fillText('通关率', statW * 2.5, 211);
      ctx.textAlign = 'left';

      // Achievements
      ctx.fillStyle = palette.textSub;
      ctx.font = 'bold 11px sans-serif';
      ctx.fillText('成就', 20, 246);

      const achW = (width - 48) / 2;
      const achievementCards = [
        { x: 20, y: 256, item: profile.achievements[0] },
        { x: 28 + achW, y: 256, item: profile.achievements[1] },
        { x: 20, y: 310, item: profile.achievements[2] },
        { x: 28 + achW, y: 310, item: profile.achievements[3] },
      ];

      achievementCards.forEach((card) => {
        const item = card.item || { title: '暂无数据', desc: '等待后端返回', active: false };
        const iconFill = item.active ? palette.successBg : palette.grayBg;
        const titleColor = item.active ? palette.success : palette.textMuted;
        const itemDesc = item.description || item.desc || '等待后端返回';

        drawRoundedRect(ctx, card.x, card.y, achW, 46, 10, palette.bgSecondary, palette.borderLight);
        ctx.beginPath(); ctx.roundRect(card.x + 6, card.y + 8, 30, 30, 6); ctx.fillStyle = iconFill; ctx.fill();
        ctx.fillStyle = titleColor; ctx.font = 'bold 11px sans-serif'; ctx.fillText(item.title || '暂无数据', card.x + 44, card.y + 18);
        ctx.fillStyle = palette.textSub; ctx.font = '9px sans-serif'; ctx.fillText(itemDesc, card.x + 44, card.y + 32);
      });

      // History
      ctx.fillStyle = palette.textSub;
      ctx.font = 'bold 11px sans-serif';
      ctx.fillText('最近对局', 20, 381);

      drawRoundedRect(ctx, 20, 391, width - 40, 100, 10, palette.bgSecondary, palette.borderLight);

      let hy = 411;
      profile.recentRuns.forEach((h, index) => {
        const dotColor = h.color || (index === 0 ? palette.warning : palette.success);
        ctx.beginPath(); ctx.arc(35, hy - 4, 3, 0, Math.PI * 2);
        ctx.fillStyle = dotColor; ctx.fill();
        ctx.fillStyle = palette.textMain; ctx.font = '11px sans-serif'; ctx.fillText(h.name || '暂无记录', 48, hy);
        ctx.fillStyle = dotColor; ctx.font = 'bold 11px sans-serif'; ctx.textAlign = 'right'; ctx.fillText(String(h.score || '--'), width - 35, hy); ctx.textAlign = 'left';
        hy += 26;
      });

      // Tab bar
      const tabWidth = width / 3;
      tabs.forEach((t, i) => {
        t.x = i * tabWidth;
        t.y = height - 60;
        t.width = tabWidth;
      });
      drawTabBar(ctx, width, height, 2);
    },

    onTap(point) {
      if (isPointInRect(point, avatarTapRect) || isPointInRect(point, avatarActionRect)) {
        app.changeAvatar();
        return;
      }

      const tappedTab = tabs.find((t) => isPointInRect(point, t));
      if (tappedTab) {
        if (tappedTab.action === 'home') {
          app.navigate('home');
        } else if (tappedTab.action === 'rank') {
          app.openRankings();
        }
      }
    },
  };
}

module.exports = {
  createChallengeScene,
};
