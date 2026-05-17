const palette = {
  bg: '#1A1A1C', // 主背景：深暗灰
  bgSecondary: '#242427', // 次背景：稍亮的暗灰（卡片/模块）
  border: '#3A3A3E', // 边框
  borderLight: '#2F2F33', // 浅色分割线
  textMain: '#E5E5E6', // 主文本：亮灰白
  textSub: '#A1A1A6', // 次文本：中灰
  textMuted: '#6B6B70', // 弱文本：深灰

  // 赛博/潜入风格主题色：荧光青/暗绿
  primary: '#00E5FF', // 主色：赛博青
  primaryDark: '#007A8A', // 深青色
  primaryLight: '#113A40', // 浅青底色：暗绿偏青
  primaryText: '#80F2FF', // 浅底色上的文字

  success: '#1EA382', // 成功文字
  successBg: '#133A30', // 成功底色
  successIcon: '#23C49D', // 成功图标

  danger: '#FF3366', // 失败/警示文字（赛博红）
  dangerBg: '#4A1120', // 失败底色
  dangerBtn: '#CC0033', // 失败按钮

  warning: '#FFB800', // 提示文字（赛博黄）
  warningBg: '#4A3500', // 提示底色
  warningIcon: '#FFCC33', // 星星颜色

  gray: '#7A7A80', // 锁定图标
  grayBg: '#2A2A2E', // 锁定底色
  grayText: '#8F8F94' // 锁定文字
};

function drawRoundedRect(ctx, x, y, width, height, radius, fillStyle, strokeStyle) {
  ctx.save();
  const safeRadius = Math.min(radius, width / 2, height / 2);
  ctx.beginPath();
  ctx.moveTo(x + safeRadius, y);
  ctx.arcTo(x + width, y, x + width, y + height, safeRadius);
  ctx.arcTo(x + width, y + height, x, y + height, safeRadius);
  ctx.arcTo(x, y + height, x, y, safeRadius);
  ctx.arcTo(x, y, x + width, y, safeRadius);
  ctx.closePath();

  if (fillStyle) {
    ctx.fillStyle = fillStyle;
    ctx.fill();
  }

  if (strokeStyle) {
    ctx.strokeStyle = strokeStyle;
    ctx.lineWidth = 2;
    ctx.stroke();
  }
  ctx.restore();
}

function drawTextBlock(ctx, text, options) {
  ctx.save();
  const {
    x,
    y,
    maxWidth,
    lineHeight,
    color,
    font,
  } = options;

  ctx.fillStyle = color || palette.text;
  ctx.font = font || '14px sans-serif';

  const chars = String(text || '').split('');
  const lines = [];
  let currentLine = '';

  chars.forEach((char) => {
    const testLine = currentLine + char;
    if (ctx.measureText(testLine).width > maxWidth && currentLine) {
      lines.push(currentLine);
      currentLine = char;
      return;
    }

    currentLine = testLine;
  });

  if (currentLine) {
    lines.push(currentLine);
  }

  lines.forEach((line, index) => {
    ctx.fillText(line, x, y + index * lineHeight);
  });

  ctx.restore();
  return lines.length;
}

function drawCircularAvatar(ctx, image, x, y, size, options = {}) {
  ctx.save();
  ctx.beginPath();
  ctx.arc(x + size / 2, y + size / 2, size / 2, 0, Math.PI * 2);
  ctx.closePath();
  ctx.clip();

  if (image) {
    ctx.drawImage(image, x, y, size, size);
    ctx.restore();
    return;
  }

  const fallbackFill = options.fallbackFill || palette.primaryLight;
  const fallbackText = options.fallbackText || '';
  const textColor = options.textColor || palette.primaryText;
  ctx.fillStyle = fallbackFill;
  ctx.fillRect(x, y, size, size);
  ctx.restore();

  if (!fallbackText) {
    return;
  }

  ctx.save();
  ctx.fillStyle = textColor;
  ctx.font = `bold ${Math.max(12, Math.floor(size * 0.38))}px sans-serif`;
  ctx.textAlign = 'center';
  ctx.textBaseline = 'middle';
  ctx.fillText(fallbackText, x + size / 2, y + size / 2);
  ctx.restore();
}

function drawHeader(ctx, width, title, subTitle = '') {
  ctx.save();
  ctx.fillStyle = palette.bg;
  ctx.fillRect(0, 0, width, 80);

  ctx.fillStyle = palette.textMain;
  ctx.font = 'bold 20px sans-serif';
  ctx.textAlign = 'left';
  ctx.textBaseline = 'alphabetic';
  ctx.fillText(title, 20, 50);

  if (subTitle) {
    ctx.fillStyle = palette.textSub;
    ctx.font = '12px sans-serif';
    ctx.fillText(subTitle, 20, 70);
  }

  // Draw bottom border
  ctx.beginPath();
  ctx.moveTo(0, 80);
  ctx.lineTo(width, 80);
  ctx.strokeStyle = palette.borderLight;
  ctx.lineWidth = 1;
  ctx.stroke();
  ctx.restore();
}

function drawButton(ctx, text, x, y, width, height, type = 'primary') {
  ctx.save();
  const isPrimary = type === 'primary';
  const isDanger = type === 'danger';
  const isGhost = type === 'ghost';

  ctx.fillStyle = isPrimary ? palette.primary : (isDanger ? palette.dangerBtn : palette.bg);
  ctx.beginPath();
  ctx.roundRect(x, y, width, height, height / 2);
  ctx.fill();

  if (isGhost) {
    ctx.strokeStyle = palette.border;
    ctx.lineWidth = 1;
    ctx.stroke();
  }

  ctx.fillStyle = (isPrimary || isDanger) ? palette.bg : palette.textMain;
  ctx.font = 'bold 16px sans-serif';
  ctx.textAlign = 'center';
  ctx.textBaseline = 'middle';
  ctx.fillText(text, x + width / 2, y + height / 2);
  ctx.restore();
}

function isPointInRect(point, rect) {
  return (
    point.x >= rect.x &&
    point.x <= rect.x + rect.width &&
    point.y >= rect.y &&
    point.y <= rect.y + rect.height
  );
}

function drawTabBar(ctx, width, height, activeIndex = 0) {
  ctx.save();
  const tabHeight = 60;
  const y = height - tabHeight;

  ctx.fillStyle = palette.bg;
  ctx.fillRect(0, y, width, tabHeight);

  ctx.beginPath();
  ctx.moveTo(0, y);
  ctx.lineTo(width, y);
  ctx.strokeStyle = palette.borderLight;
  ctx.lineWidth = 1;
  ctx.stroke();

  const tabs = ['关卡', '排行榜', '我的'];
  const tabWidth = width / 3;

  tabs.forEach((tab, index) => {
    const isAct = index === activeIndex;
    ctx.fillStyle = isAct ? palette.primary : palette.textMuted;
    ctx.font = isAct ? 'bold 12px sans-serif' : '12px sans-serif';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'alphabetic';
    ctx.fillText(tab, index * tabWidth + tabWidth / 2, y + 35);

    // Draw icon placeholder
    ctx.beginPath();
    ctx.arc(index * tabWidth + tabWidth / 2, y + 18, 8, 0, Math.PI * 2);
    if (isAct) {
      ctx.fill();
    } else {
      ctx.strokeStyle = palette.textMuted;
      ctx.lineWidth = 1.5;
      ctx.stroke();
    }
  });
  ctx.restore();
}

module.exports = {
  palette,
  drawRoundedRect,
  drawTextBlock,
  drawCircularAvatar,
  drawButton,
  isPointInRect,
  drawHeader,
  drawTabBar,
};
