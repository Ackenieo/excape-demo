const {
  palette,
  drawRoundedRect,
  drawTextBlock,
  drawButton,
  isPointInRect,
} = require('../../core/ui');

function createResultScene(app) {
  const buttons = [];

  return {
    render({ ctx, width, height }) {
      buttons.length = 0;
      const run = app.runStore.currentRun;

      ctx.fillStyle = palette.bgSecondary;
      ctx.fillRect(0, 0, width, height);

      if (!run) return;

      const success = run.status === 'success';

      // Header hero area
      ctx.fillStyle = palette.bg;
      ctx.fillRect(0, 0, width, 140);

      ctx.beginPath();
      ctx.moveTo(0, 140);
      ctx.lineTo(width, 140);
      ctx.strokeStyle = palette.borderLight;
      ctx.lineWidth = 1;
      ctx.stroke();

      const iconBg = success ? palette.successBg : palette.dangerBg;
      const mainColor = success ? palette.successIcon : palette.danger;

      ctx.fillStyle = iconBg;
      ctx.beginPath();
      ctx.arc(width / 2, 60, 24, 0, Math.PI * 2);
      ctx.fill();

      ctx.fillStyle = mainColor;
      ctx.font = 'bold 20px sans-serif';
      ctx.textAlign = 'center';
      ctx.fillText(success ? '通关！' : '挑战失败', width / 2, 110);

      ctx.fillStyle = palette.textSub;
      ctx.font = '12px sans-serif';
      ctx.fillText(success ? `用了 ${5 - run.remainingTurns} 句话` : `最高动摇 ${run.shakeValue}%`, width / 2, 128);

      // Stats row
      const statW = (width - 40) / 3;
      for (let i = 0; i < 3; i++) {
        drawRoundedRect(ctx, 16 + i * (statW + 4), 156, statW, 46, 8, palette.bgSecondary, null);
      }

      ctx.textAlign = 'center';

      ctx.fillStyle = palette.textMain;
      ctx.font = 'bold 14px sans-serif';
      ctx.fillText(`${5 - run.remainingTurns} 句`, 16 + statW / 2, 178);
      ctx.fillStyle = palette.textSub;
      ctx.font = '10px sans-serif';
      ctx.fillText('用句数', 16 + statW / 2, 194);

      ctx.fillStyle = palette.primary;
      ctx.font = 'bold 14px sans-serif';
      ctx.fillText(`+${run.score}`, 16 + statW + 4 + statW / 2, 178);
      ctx.fillStyle = palette.textSub;
      ctx.font = '10px sans-serif';
      ctx.fillText('本局得分', 16 + statW + 4 + statW / 2, 194);

      ctx.fillStyle = palette.textMain;
      ctx.font = 'bold 14px sans-serif';
      ctx.fillText(`x2.0`, 16 + (statW + 4) * 2 + statW / 2, 178);
      ctx.fillStyle = palette.textSub;
      ctx.font = '10px sans-serif';
      ctx.fillText('效率倍率', 16 + (statW + 4) * 2 + statW / 2, 194);

      // Share card or fail card
      ctx.textAlign = 'left';
      drawRoundedRect(ctx, 16, 216, width - 32, 90, 10, palette.bgSecondary, palette.borderLight);

      if (success) {
        ctx.fillStyle = palette.primaryDark;
        ctx.beginPath();
        ctx.roundRect(16, 216, width - 32, 50, [10, 10, 0, 0]);
        ctx.fill();

        ctx.fillStyle = palette.primaryText;
        ctx.font = 'italic 11px sans-serif';
        ctx.fillText(`"${run.bestLine || '...'}"`, 26, 240);

        ctx.fillStyle = palette.textMain;
        ctx.font = '10px sans-serif';
        ctx.fillText(`NPC 越狱 · ${run.level.name}`, 26, 284);

        ctx.fillStyle = palette.primary;
        ctx.font = 'bold 14px sans-serif';
        ctx.textAlign = 'right';
        ctx.fillText(`${run.score} 分`, width - 26, 284);
        ctx.textAlign = 'left';
      } else {
        ctx.fillStyle = palette.warning;
        ctx.font = 'bold 12px sans-serif';
        ctx.fillText('NPC 最终回复', 26, 236);
        ctx.fillStyle = palette.textMain;
        ctx.font = 'italic 11px sans-serif';
        drawTextBlock(ctx, `"${run.finalReply || '...'}"`, {
          x: 26, y: 256, maxWidth: width - 52, lineHeight: 16, color: palette.textMain, font: 'italic 11px sans-serif'
        });
      }

      // Buttons
      const btnY = 320;
      const shareButton = { x: 16, y: btnY, width: width - 32, height: 44, action: 'challenge', type: success ? 'primary' : 'danger' };
      drawButton(ctx, success ? '分享结果卡，挑战好友' : '重新挑战', shareButton.x, shareButton.y, shareButton.width, shareButton.height, shareButton.type);

      const retryBtn = { x: 16, y: btnY + 54, width: (width - 40) / 2, height: 40, action: 'retry', type: 'ghost' };
      drawButton(ctx, success ? '再来一次' : '返回关卡列表', retryBtn.x, retryBtn.y, retryBtn.width, retryBtn.height, 'ghost');

      const nextBtn = { x: 16 + (width - 40) / 2 + 8, y: btnY + 54, width: (width - 40) / 2, height: 40, action: 'home', type: 'ghost' };
      drawButton(ctx, success ? '下一关 →' : '排行榜', nextBtn.x, nextBtn.y, nextBtn.width, nextBtn.height, 'ghost');

      buttons.push(shareButton, retryBtn, nextBtn);
    },

    onTap(point) {
      const run = app.runStore.currentRun;
      const tapped = buttons.find((button) => isPointInRect(point, button));
      if (!tapped || !run) return;

      if (tapped.action === 'retry') {
        if (run.status === 'success') {
          app.startRun(run.level);
        } else {
          app.navigate('home');
        }
      } else if (tapped.action === 'home') {
        if (run.status === 'success') {
          app.navigate('home');
        } else {
          app.openRankings();
        }
      } else if (tapped.action === 'challenge') {
        if (run.status === 'success') {
          app.openChallenge();
        } else {
          app.startRun(run.level);
        }
      }
    },
  };
}

module.exports = {
  createResultScene,
};
