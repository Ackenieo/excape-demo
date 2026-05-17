const {
  palette,
  drawRoundedRect,
  drawTextBlock,
  drawButton,
  isPointInRect,
  drawHeader,
  drawTabBar,
} = require('../../core/ui');

function createHomeScene(app) {
  const buttons = [];
  const tabs = [
    { x: 0, y: 0, width: 0, height: 60, action: 'home' },
    { x: 0, y: 0, width: 0, height: 60, action: 'rank' },
    { x: 0, y: 0, width: 0, height: 60, action: 'profile' }
  ];

  return {
    render({ ctx, width, height }) {
      buttons.length = 0;
      ctx.fillStyle = palette.bgSecondary;
      ctx.fillRect(0, 0, width, height);

      drawHeader(
        ctx,
        width,
        'NPC 越狱',
        '选择关卡，或创建自定义 AI NPC',
      );

      // Stats row
      ctx.fillStyle = palette.bgSecondary;
      ctx.fillRect(0, 80, width, 60);

      const cardWidth = width - 24;
      let currentY = 100;
      const customNpc = app.appStore.customNpc;

      const customEntryCard = {
        x: 12,
        y: currentY,
        width: cardWidth,
        height: 72,
        action: 'customNpc',
      };
      buttons.push(customEntryCard);
      drawRoundedRect(
        ctx,
        customEntryCard.x,
        customEntryCard.y,
        customEntryCard.width,
        customEntryCard.height,
        12,
        palette.bg,
        palette.primaryDark,
      );
      ctx.fillStyle = palette.primary;
      ctx.font = 'bold 15px sans-serif';
      ctx.fillText('创建自定义 AI NPC', customEntryCard.x + 16, customEntryCard.y + 26);
      ctx.fillStyle = palette.textSub;
      ctx.font = '11px sans-serif';
      ctx.fillText('自定义名称、身份、性格和开场白', customEntryCard.x + 16, customEntryCard.y + 46);
      ctx.textAlign = 'right';
      ctx.fillStyle = palette.primary;
      ctx.fillText('去创建', customEntryCard.x + customEntryCard.width - 16, customEntryCard.y + 38);
      ctx.textAlign = 'left';
      currentY += 82;

      if (customNpc && customNpc.npcId) {
        const recentNpcCard = {
          x: 12,
          y: currentY,
          width: cardWidth,
          height: 82,
          action: 'startCustomNpc',
        };
        buttons.push(recentNpcCard);
        drawRoundedRect(
          ctx,
          recentNpcCard.x,
          recentNpcCard.y,
          recentNpcCard.width,
          recentNpcCard.height,
          12,
          palette.bgSecondary,
          palette.borderLight,
        );

        ctx.fillStyle = palette.warningIcon;
        ctx.font = '10px sans-serif';
        ctx.fillText('最近创建', recentNpcCard.x + 16, recentNpcCard.y + 18);
        ctx.fillStyle = palette.textMain;
        ctx.font = 'bold 15px sans-serif';
        ctx.fillText(customNpc.name || '自定义 NPC', recentNpcCard.x + 16, recentNpcCard.y + 40);
        ctx.fillStyle = palette.textSub;
        ctx.font = '11px sans-serif';
        ctx.fillText(customNpc.role || '自定义身份', recentNpcCard.x + 16, recentNpcCard.y + 60);
        ctx.textAlign = 'right';
        ctx.fillStyle = palette.primary;
        ctx.fillText('尝试开局', recentNpcCard.x + recentNpcCard.width - 16, recentNpcCard.y + 44);
        ctx.textAlign = 'left';
        currentY += 92;
      }

      app.appStore.levels.forEach((level) => {
        const card = {
          x: 12,
          y: currentY,
          width: cardWidth,
          height: 90,
          levelId: level.id,
        };

        buttons.push(card);
        drawRoundedRect(ctx, card.x, card.y, card.width, card.height, 12, palette.bgSecondary, palette.borderLight);

        ctx.fillStyle = palette.textMain;
        ctx.font = 'bold 16px sans-serif';
        ctx.fillText(level.name, card.x + 16, card.y + 26);

        ctx.fillStyle = palette.textSub;
        ctx.font = '12px sans-serif';
        ctx.fillText(`难度 ${level.difficulty} · ${level.goal}`, card.x + 16, card.y + 46);

        // Card Footer
        ctx.fillStyle = palette.bgSecondary;
        ctx.beginPath();
        ctx.roundRect(card.x, card.y + 60, card.width, 30, [0, 0, 12, 12]);
        ctx.fill();

        ctx.fillStyle = palette.textMuted;
        ctx.font = '11px sans-serif';
        ctx.fillText(level.intro, card.x + 16, card.y + 78);

        currentY += 100;
      });

      // Update tabs hitboxes
      const tabWidth = width / 3;
      tabs.forEach((t, i) => {
        t.x = i * tabWidth;
        t.y = height - 60;
        t.width = tabWidth;
      });
      drawTabBar(ctx, width, height, 0);
    },

    onTap(point) {
      // Check tabs
      const tappedTab = tabs.find((t) => isPointInRect(point, t));
      if (tappedTab) {
        if (tappedTab.action === 'rank') {
          app.openRankings();
        } else if (tappedTab.action === 'profile') {
          app.openChallenge();
        }
        return;
      }

      const customNpcButton = buttons.find((button) => button.action === 'customNpc' && isPointInRect(point, button));
      if (customNpcButton) {
        app.openCustomNpc();
        return;
      }

      const customNpcStartButton = buttons.find((button) => button.action === 'startCustomNpc' && isPointInRect(point, button));
      if (customNpcStartButton) {
        app.startCustomNpc(app.appStore.customNpc);
        return;
      }

      const tapped = buttons.find((button) => isPointInRect(point, button));
      if (!tapped) {
        return;
      }

      const level = app.appStore.levels.find((item) => item.id === tapped.levelId);
      if (level) {
        app.startRun(level);
      }
    },
  };
}

module.exports = {
  createHomeScene,
};
