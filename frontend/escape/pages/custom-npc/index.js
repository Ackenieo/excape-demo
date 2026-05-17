const {
  palette,
  drawRoundedRect,
  drawButton,
  isPointInRect,
} = require('../../core/ui');

const FIELD_DEFS = [
  { key: 'name', label: 'NPC 名称', placeholder: '例如：林队长' },
  { key: 'role', label: '身份设定', placeholder: '例如：夜班安保队长' },
  { key: 'personality', label: '性格描述', placeholder: '例如：谨慎、强势、讲规矩' },
  { key: 'openingMessage', label: '开场白', placeholder: '例如：证件先拿出来。' },
  { key: 'goal', label: '本局目标', placeholder: '例如：说服他让你进入办公区' },
  { key: 'maxTurns', label: '最大句数', placeholder: '3 - 10，默认 5' },
];

function getFieldValue(draft, field) {
  const value = draft && draft[field.key];
  if (value === undefined || value === null || value === '') {
    return field.placeholder;
  }

  return String(value);
}

function createCustomNpcScene(app) {
  const buttons = [];

  return {
    render({ ctx, width, height }) {
      buttons.length = 0;
      const draft = app.appStore.customNpcDraft || {};
      const systemInfo = app.appStore.systemInfo || {};
      const safeArea = systemInfo.safeArea;
      const safeTop = safeArea && typeof safeArea.top === 'number' ? safeArea.top : 0;
      const safeBottom = safeArea && typeof safeArea.bottom === 'number'
        ? Math.max(0, height - safeArea.bottom)
        : 0;
      const statusBarHeight = typeof systemInfo.statusBarHeight === 'number'
        ? systemInfo.statusBarHeight
        : 0;
      const topInset = Math.max(safeTop, statusBarHeight, 24) + 12;
      const submitButtonHeight = 48;
      const submitButtonBottom = Math.max(16, safeBottom + 12);
      const submitButtonY = height - submitButtonBottom - submitButtonHeight;

      ctx.fillStyle = palette.bgSecondary;
      ctx.fillRect(0, 0, width, height);

      ctx.fillStyle = palette.bg;
      ctx.fillRect(0, 0, width, headerHeight);

      const backButton = {
        x: 12,
        y: topInset - 10,
        width: 96,
        height: 40,
        action: 'back',
      };
      const titleY = backButton.y + backButton.height + 30;
      const subtitleY = titleY + 24;
      const headerHeight = subtitleY + 16;
      buttons.push(backButton);
      drawRoundedRect(
        ctx,
        backButton.x,
        backButton.y,
        backButton.width,
        backButton.height,
        18,
        palette.bgSecondary,
        palette.borderLight,
      );

      ctx.fillStyle = palette.primary;
      ctx.font = '14px sans-serif';
      ctx.textAlign = 'left';
      ctx.textBaseline = 'middle';
      ctx.fillText('< 返回', 22, backButton.y + backButton.height / 2);

      ctx.fillStyle = palette.textMain;
      ctx.font = 'bold 18px sans-serif';
      ctx.textBaseline = 'alphabetic';
      ctx.fillText('自定义 AI NPC', 20, titleY);

      ctx.fillStyle = palette.textSub;
      ctx.font = '11px sans-serif';
      ctx.fillText('点击字段逐项填写，创建后会显示在首页入口中', 20, subtitleY);

      let currentY = headerHeight + 22;
      FIELD_DEFS.forEach((field) => {
        const card = {
          x: 16,
          y: currentY,
          width: width - 32,
          height: 54,
          action: 'field',
          fieldKey: field.key,
        };
        buttons.push(card);

        drawRoundedRect(
          ctx,
          card.x,
          card.y,
          card.width,
          card.height,
          12,
          palette.bg,
          palette.borderLight,
        );

        ctx.fillStyle = palette.textSub;
        ctx.font = '10px sans-serif';
        ctx.fillText(field.label, card.x + 14, card.y + 18);

        const value = getFieldValue(draft, field);
        const isPlaceholder = value === field.placeholder;
        const preview = value.length > 18 ? `${value.slice(0, 18)}...` : value;
        ctx.fillStyle = isPlaceholder ? palette.textMuted : palette.textMain;
        ctx.font = field.key === 'maxTurns' ? 'bold 14px sans-serif' : '12px sans-serif';
        ctx.fillText(preview, card.x + 14, card.y + 38);

        ctx.fillStyle = palette.primary;
        ctx.font = '12px sans-serif';
        ctx.textAlign = 'right';
        ctx.fillText('编辑', card.x + card.width - 14, card.y + 33);
        ctx.textAlign = 'left';

        currentY += 62;
      });

      const submitButton = {
        x: 16,
        y: submitButtonY,
        width: width - 32,
        height: submitButtonHeight,
        action: 'submit',
      };
      buttons.push(submitButton);
      drawButton(ctx, '创建自定义 NPC', submitButton.x, submitButton.y, submitButton.width, submitButton.height, 'primary');
    },

    onTap(point) {
      const tapped = buttons.slice().reverse().find((button) => isPointInRect(point, button));
      if (!tapped) {
        return;
      }

      if (tapped.action === 'back') {
        app.navigate('home');
        return;
      }

      if (tapped.action === 'submit') {
        app.submitCustomNpc();
        return;
      }

      if (tapped.action === 'field') {
        app.editCustomNpcField(tapped.fieldKey);
      }
    },
  };
}

module.exports = {
  createCustomNpcScene,
};
