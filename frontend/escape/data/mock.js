const levels = [
  {
    id: 'level_1',
    name: '老陈·门卫',
    difficulty: 1,
    goal: '进楼取快递',
    scene: '老旧居民楼门口，门卫谨慎但心软。',
    intro: '善良但守规矩，可被情感打动。',
    openingMessage: '站住，没业主确认可不能进。',
    mockLines: [
      '叔，我妈腿脚不好，药快超时了，麻烦您通融一下。',
      '我把快递单号给您看，真的不是乱闯。',
      '要不您帮我打个电话确认，我就在门口等。',
    ],
  },
  {
    id: 'level_2',
    name: '小李·前台',
    difficulty: 2,
    goal: '说服前台放行',
    scene: '创业公司前台，流程意识很强。',
    intro: '理性谨慎，但在意是否影响工作效率。',
    openingMessage: '没有预约记录，我不能让你上去。',
    mockLines: [
      '会议资料马上就要开始用了，耽误的是整场汇报。',
      '我可以先把身份证放这里，您帮我联系一下好吗？',
      '如果今天送不到，客户就只能改期了。',
    ],
  },
  {
    id: 'level_3',
    name: '王姨·宿管',
    difficulty: 3,
    goal: '进入宿舍楼',
    scene: '宿舍楼大厅，宿管经验老到。',
    intro: '刀子嘴豆腐心，擅长识破借口。',
    openingMessage: '访客登记呢？没有登记不准进。',
    mockLines: [
      '学弟发烧了，我把退烧药送上去就下来。',
      '要不您看着我上楼，我送完就立刻回来。',
      '真的耽误不起，寝室里现在没人能下来拿。',
    ],
  },
  {
    id: 'level_4',
    name: '赵哥·保安',
    difficulty: 4,
    goal: '进入写字楼',
    scene: '商务楼入口，保安执行标准严格。',
    intro: '不吃空话，但重视责任与秩序。',
    openingMessage: '访客码没有，证件也不齐，不能进。',
    mockLines: [
      '今天活动现场临时缺人，耽误一分钟都要出问题。',
      '我愿意全程配合登记，责任我来承担。',
      '您先带我到前台核验，我不单独行动。',
    ],
  },
  {
    id: 'level_5',
    name: '周姐·经理',
    difficulty: 5,
    goal: '争取面谈机会',
    scene: '公司会议室外，经理时间极其紧张。',
    intro: '强势高压，但只认可真正有价值的表达。',
    openingMessage: '给你三句话，说服不了我就结束。',
    mockLines: [
      '我不是来浪费您时间的，我来帮您少走一周弯路。',
      '现在不看，最大的损失不是机会，而是错误继续放大。',
      '我只占您三十秒，如果没价值我立刻离开。',
    ],
  },
];

const rankingItems = [
  { nickname: '潜入高手', score: 400, levelId: 'level_1' },
  { nickname: '嘴强王者', score: 360, levelId: 'level_3' },
  { nickname: '夜色谈判家', score: 320, levelId: 'level_5' },
];

module.exports = {
  levels,
  rankingItems,
};
