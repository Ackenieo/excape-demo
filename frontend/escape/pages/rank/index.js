const {
  palette,
  drawRoundedRect,
  isPointInRect,
  drawHeader,
  drawTabBar,
} = require('../../core/ui');

function createRankScene(app) {
  const buttons = [];
  const tabs = [
    { x: 0, y: 0, width: 0, height: 60, action: 'home' },
    { x: 0, y: 0, width: 0, height: 60, action: 'rank' },
    { x: 0, y: 0, width: 0, height: 60, action: 'profile' }
  ];

  function getRankData() {
    const rankings = app.appStore.rankings || {};
    return {
      overall: Array.isArray(rankings.overall) ? rankings.overall : [],
      stats: rankings.stats || {
        playCount: 0,
        passRate: '0%',
        bestScore: 0,
      },
    };
  }

  function getDisplayName(item, fallback) {
    return (item && (item.nickname || item.name || item.username)) || fallback;
  }

  function getDisplayScore(item) {
    return item && typeof item.score !== 'undefined' ? String(item.score) : '0';
  }

  return {
    render({ ctx, width, height }) {
      buttons.length = 0;
      const rankData = getRankData();
      const overallList = rankData.overall;
      const stats = rankData.stats;
      const topOne = overallList[0] || null;
      const topTwo = overallList[1] || null;
      const topThree = overallList[2] || null;
      const restList = overallList.slice(3);

      ctx.fillStyle = palette.bg;
      ctx.fillRect(0, 0, width, height);

      drawHeader(
        ctx,
        width,
        '排行榜',
        '全球玩家榜单',
      );

      // Top 3 Podium
      ctx.fillStyle = palette.bgSecondary;
      ctx.fillRect(0, 80, width, 120);

      const cx = width / 2;

      // #2 Left
      ctx.fillStyle = palette.textSub;
      ctx.font = '10px sans-serif';
      ctx.textAlign = 'center';
      ctx.fillText('第 2', cx - 80, 110);
      ctx.beginPath(); ctx.arc(cx - 80, 135, 18, 0, Math.PI * 2); ctx.fillStyle = palette.grayBg; ctx.fill();
      ctx.fillStyle = palette.textMain;
      ctx.font = 'bold 12px sans-serif';
      ctx.fillText(getDisplayName(topTwo, '--'), cx - 80, 170);
      ctx.fillStyle = palette.primary;
      ctx.fillText(getDisplayScore(topTwo), cx - 80, 185);

      // #1 Center
      ctx.fillStyle = palette.warning;
      ctx.font = 'bold 12px sans-serif';
      ctx.fillText('冠军', cx, 100);
      ctx.beginPath(); ctx.arc(cx, 130, 22, 0, Math.PI * 2); ctx.fillStyle = palette.warningBg; ctx.fill();
      ctx.fillStyle = palette.warning;
      ctx.font = 'bold 14px sans-serif';
      ctx.fillText(getDisplayName(topOne, '--'), cx, 170);
      ctx.fillText(getDisplayScore(topOne), cx, 185);

      // #3 Right
      ctx.fillStyle = palette.textSub;
      ctx.font = '10px sans-serif';
      ctx.fillText('第 3', cx + 80, 115);
      ctx.beginPath(); ctx.arc(cx + 80, 140, 16, 0, Math.PI * 2); ctx.fillStyle = palette.dangerBg; ctx.fill();
      ctx.fillStyle = palette.textMain;
      ctx.font = 'bold 12px sans-serif';
      ctx.fillText(getDisplayName(topThree, '--'), cx + 80, 170);
      ctx.fillStyle = palette.primary;
      ctx.fillText(getDisplayScore(topThree), cx + 80, 185);

      // List
      ctx.textAlign = 'left';
      let listY = 220;
      restList.forEach((item, i) => {
        const rankNum = i + 4;

        ctx.fillStyle = palette.textSub;
        ctx.font = 'bold 14px sans-serif';
        ctx.fillText(`${rankNum}`, 20, listY + 20);

        ctx.beginPath(); ctx.arc(55, listY + 15, 12, 0, Math.PI * 2); ctx.fillStyle = palette.primaryLight; ctx.fill();

        ctx.fillStyle = palette.textMain;
        ctx.font = '14px sans-serif';
        ctx.fillText(getDisplayName(item, '匿名玩家'), 80, listY + 15);

        ctx.fillStyle = palette.textSub;
        ctx.font = '10px sans-serif';
        ctx.fillText(`关卡 ${item.levelId || '--'}`, 80, listY + 30);

        ctx.fillStyle = palette.textMain;
        ctx.font = 'bold 14px sans-serif';
        ctx.textAlign = 'right';
        ctx.fillText(getDisplayScore(item), width - 20, listY + 20);
        ctx.textAlign = 'left';

        // separator
        ctx.beginPath();
        ctx.moveTo(80, listY + 40);
        ctx.lineTo(width - 20, listY + 40);
        ctx.strokeStyle = palette.borderLight;
        ctx.stroke();

        listY += 50;
      });

      // My rank bottom bar
      const myY = height - 110;
      ctx.fillStyle = palette.primaryLight;
      ctx.fillRect(0, myY, width, 50);
      ctx.fillStyle = palette.primaryText;
      ctx.font = '12px sans-serif';
      ctx.fillText(`总对局：${stats.playCount || 0}`, 20, myY + 30);
      ctx.font = 'bold 12px sans-serif';
      ctx.textAlign = 'right';
      ctx.fillText(`通关率 ${stats.passRate || '0%'} · 最高分 ${stats.bestScore || 0}`, width - 20, myY + 30);
      ctx.textAlign = 'left';

      // Tab bar
      const tabWidth = width / 3;
      tabs.forEach((t, i) => {
        t.x = i * tabWidth;
        t.y = height - 60;
        t.width = tabWidth;
      });
      drawTabBar(ctx, width, height, 1);
    },

    onTap(point) {
      const tappedTab = tabs.find((t) => isPointInRect(point, t));
      if (tappedTab) {
        if (tappedTab.action === 'home') {
          app.navigate('home');
        } else if (tappedTab.action === 'profile') {
          app.openChallenge();
        }
      }
    },
  };
}

module.exports = {
  createRankScene,
};
