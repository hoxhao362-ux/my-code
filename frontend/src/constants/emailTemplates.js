export const PLATFORM_NAME = '柳叶刀投稿平台';
export const PLATFORM_DOMAIN = 'journal-submit.com'; // Example domain
export const BRAND_RED = '#C93737';
export const DARK_GRAY = '#333333';
export const LIGHT_GRAY = '#999999';
export const BG_WHITE = '#FFFFFF';

const BASE_STYLES = `
  font-family: 'Times New Roman', serif, 'SimSun', sans-serif;
  color: ${DARK_GRAY};
  line-height: 1.5;
  margin: 0;
  padding: 0;
  background-color: ${BG_WHITE};
`;

const BUTTON_BASE = `
  display: inline-block;
  padding: 12px 24px;
  font-size: 16px;
  font-weight: bold;
  text-decoration: none;
  border-radius: 4px;
  text-align: center;
  margin: 10px 0;
`;

const BUTTON_PRIMARY = `
  ${BUTTON_BASE}
  background-color: ${BRAND_RED};
  color: #FFFFFF;
`;

const BUTTON_SECONDARY = `
  ${BUTTON_BASE}
  background-color: #E0E0E0;
  color: ${DARK_GRAY};
`;

const HEADER = `
  <div style="text-align: center; padding: 20px 0; border-bottom: 1px solid #E0E0E0;">
    <div style="font-size: 24px; font-weight: bold; color: ${DARK_GRAY};">
      <span style="color: ${BRAND_RED};">The Lancet</span> | ${PLATFORM_NAME}
    </div>
    <div style="font-size: 12px; color: ${LIGHT_GRAY}; margin-top: 5px;">
      期刊投稿与同行评审平台
    </div>
  </div>
`;

const FOOTER = `
  <div style="margin-top: 40px; padding-top: 20px; border-top: 1px solid #E0E0E0; text-align: center; font-size: 11px; color: ${LIGHT_GRAY};">
    <p style="margin: 5px 0;">
      您的个人数据将按照 <a href="#" style="color: ${BRAND_RED}; text-decoration: none;">${PLATFORM_NAME} 隐私政策</a> 进行处理。
    </p>
    <p style="margin: 5px 0;">
      &copy; 2026 ${PLATFORM_NAME}. 保留所有权利。
    </p>
    <p style="margin: 5px 0;">
      如果您有任何问题，请联系我们的编辑团队：<a href="mailto:editorial@${PLATFORM_DOMAIN}" style="color: ${LIGHT_GRAY}; text-decoration: none;">editorial@${PLATFORM_DOMAIN}</a>
    </p>
  </div>
`;

export const EMAIL_TEMPLATES = {
  // Reviewer Invitation Email
  reviewerInvitation: {
    subject: `审稿邀请 [稿件编号]: [稿件标题] - ${PLATFORM_NAME}`,
    content: `
      <!DOCTYPE html>
      <html>
      <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>审稿邀请</title>
        <style>
          /* Mobile Responsiveness */
          @media screen and (max-width: 600px) {
            .container { width: 100% !important; padding: 10px !important; }
            .btn { display: block !important; width: 100% !important; box-sizing: border-box; margin-bottom: 10px; }
          }
          a:hover { text-decoration: underline !important; }
          .btn-primary:hover { background-color: #B02E2E !important; }
          .btn-secondary:hover { background-color: #D0D0D0 !important; }
        </style>
      </head>
      <body style="${BASE_STYLES}">
        <div class="container" style="max-width: 600px; margin: 0 auto; padding: 20px;">
          
          ${HEADER}

          <div style="padding: 20px 0;">
            <p style="font-size: 14px; margin-bottom: 15px;">
              尊敬的 [Reviewer Full Name] 教授/博士：
            </p>
            <p style="font-size: 14px; margin-bottom: 15px;">
              我们代表 <strong>${PLATFORM_NAME} 编辑团队</strong> 写信邀请您审阅一篇稿件。鉴于您在 [Relevant Field, e.g., cardiovascular research] 领域的专业知识，作者推荐您作为潜在的审稿人。
            </p>
            
            <p style="font-size: 14px; margin-bottom: 15px;">
              This invitation is extended in line with our double-blind peer review standards, and we would greatly appreciate your academic support. The key information of the manuscript and review requirements is as follows:
            </p>

            <div style="background-color: #F9F9F9; padding: 15px; border-radius: 4px; margin-bottom: 20px;">
              <p style="margin: 5px 0; font-size: 14px;"><strong>稿件编号：</strong> [Manuscript ID]</p>
              <p style="margin: 5px 0; font-size: 14px;"><strong>稿件标题：</strong> [Manuscript Title]</p>
              <p style="margin: 5px 0; font-size: 14px;"><strong>投稿日期：</strong> [Submission Date]</p>
              <p style="margin: 5px 0; font-size: 14px;"><strong>评审类型：</strong> 双盲同行评审（所有作者身份信息已完全匿名）</p>
              <p style="margin: 5px 0; font-size: 14px;"><strong>评审截止日期：</strong> [Due Date]</p>
              <p style="margin: 5px 0; font-size: 14px;"><strong>预计投入时间：</strong> 约 2-3 小时以完成评审表并提交专业反馈</p>
            </div>

            <p style="font-size: 14px; margin-bottom: 15px;">
              由于您尚未在 <strong>${PLATFORM_NAME}</strong> 平台注册为审稿人，您需要完成免费且快速的注册以接受邀请并访问匿名稿件。注册仅需填写基本学术信息，耗时约 3-5 分钟。
            </p>
            
            <div style="text-align: center; margin: 30px 0;">
              <a href="#" class="btn btn-primary" style="${BUTTON_PRIMARY}">接受邀请并注册</a>
              <a href="#" class="btn btn-secondary" style="${BUTTON_SECONDARY} margin-left: 10px;">拒绝邀请</a>
            </div>

            <p style="font-size: 12px; color: ${LIGHT_GRAY}; text-align: center; margin-top: 10px;">
              如果上方按钮无法点击，请复制并粘贴相应链接到您的浏览器中：<br>
              接受：[Accept Link]<br>
              拒绝：[Decline Link]
            </p>
          </div>

          <div style="margin-top: 40px; padding-top: 20px; border-top: 1px solid #E0E0E0; text-align: center; font-size: 11px; color: ${LIGHT_GRAY};">
            <p style="margin: 5px 0;">
              您的个人数据将按照 <a href="#" style="color: ${BRAND_RED}; text-decoration: none;">${PLATFORM_NAME} 隐私政策</a> 进行处理。
            </p>
            <p style="margin: 5px 0;">
              接受此邀请即表示您确认与该稿件无利益冲突，并同意遵守平台的同行评审准则。
            </p>
            <p style="margin: 5px 0;">
              &copy; 2026 ${PLATFORM_NAME}. 保留所有权利。
            </p>
            <p style="margin: 5px 0;">
              如果您有任何问题，请联系我们的编辑团队：<a href="mailto:editorial@${PLATFORM_DOMAIN}" style="color: ${LIGHT_GRAY}; text-decoration: none;">editorial@${PLATFORM_DOMAIN}</a>
            </p>
          </div>

        </div>
      </body>
      </html>
    `
  },

  // Writer Recommendation Results Notification Email
  recommendationResults: {
    subject: `审稿人推荐决定 – 稿件 [Manuscript ID]: [Manuscript Title] - ${PLATFORM_NAME}`,
    content: `
      <!DOCTYPE html>
      <html>
      <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>审稿人推荐结果</title>
        <style>
          /* Mobile Responsiveness */
          @media screen and (max-width: 600px) {
            .container { width: 100% !important; padding: 10px !important; }
            .btn { display: block !important; width: 100% !important; box-sizing: border-box; }
          }
          a:hover { text-decoration: underline !important; }
          .btn-primary:hover { background-color: #B02E2E !important; }
        </style>
      </head>
      <body style="${BASE_STYLES}">
        <div class="container" style="max-width: 600px; margin: 0 auto; padding: 20px;">
          
          ${HEADER}

          <div style="padding: 20px 0;">
            <p style="font-size: 14px; margin-bottom: 15px;">
              尊敬的 [Corresponding Writer Full Name]：
            </p>
            <p style="font-size: 14px; margin-bottom: 15px;">
              我们已完成对您为投稿至 <strong>${PLATFORM_NAME}</strong> 的稿件所推荐审稿人的编辑审查。详细决定结果如下：
            </p>
            
            <div style="margin-bottom: 20px;">
               <p style="margin: 0 0 10px 0; font-size: 14px; font-weight: bold; color: ${DARK_GRAY}; border-bottom: 1px solid #eee; padding-bottom: 5px;">稿件基本信息</p>
               <p style="margin: 5px 0; font-size: 14px;"><strong>稿件编号：</strong> [Manuscript ID]</p>
               <p style="margin: 5px 0; font-size: 14px;"><strong>稿件标题：</strong> [Manuscript Title]</p>
               <p style="margin: 5px 0; font-size: 14px;"><strong>推荐提交时间：</strong> [Submission Time]</p>
            </div>

            <div style="background-color: #F9F9F9; padding: 15px; border-radius: 4px; margin-bottom: 20px;">
              <p style="margin: 0 0 15px 0; font-size: 14px; font-weight: bold; color: ${DARK_GRAY};">审稿人推荐结果</p>
              
              <div style="margin-bottom: 15px; padding-bottom: 10px; border-bottom: 1px dashed #ddd;">
                <p style="margin: 0 0 5px 0; font-size: 14px; font-weight: bold;">Dr. [Reviewer Name 1]</p>
                <p style="margin: 0 0 5px 0; font-size: 14px; color: #555;">所属机构：[Reviewer Affiliation 1]</p>
                <p style="margin: 0 0 5px 0; font-size: 14px; color: ${BRAND_RED}; font-weight: bold;">编辑决定：通过</p>
                <p style="margin: 0; font-size: 14px; color: #555;">邀请状态：邀请已于 [Date] 发送</p>
              </div>

              <div style="margin-bottom: 15px; padding-bottom: 10px; border-bottom: 1px dashed #ddd;">
                <p style="margin: 0 0 5px 0; font-size: 14px; font-weight: bold;">Dr. [Reviewer Name 2]</p>
                <p style="margin: 0 0 5px 0; font-size: 14px; color: #555;">所属机构：[Reviewer Affiliation 2]</p>
                <p style="margin: 0 0 5px 0; font-size: 14px; color: ${BRAND_RED}; font-weight: bold;">编辑决定：通过</p>
                <p style="margin: 0; font-size: 14px; color: #555;">邀请状态：邀请将在 1 个工作日内发送</p>
              </div>

              <div style="margin-bottom: 5px;">
                <p style="margin: 0 0 5px 0; font-size: 14px; font-weight: bold;">Dr. [Reviewer Name 3]</p>
                <p style="margin: 0 0 5px 0; font-size: 14px; color: #555;">所属机构：[Reviewer Affiliation 3]</p>
                <p style="margin: 0 0 5px 0; font-size: 14px; color: #999; font-weight: bold;">编辑决定：拒绝</p>
                <p style="margin: 0; font-size: 14px; color: #555;">拒绝原因：[Objective reason, e.g., potential conflict of interest, research field mismatch]</p>
              </div>
            </div>

            <div style="margin-bottom: 20px;">
               <p style="margin: 0 0 10px 0; font-size: 14px; font-weight: bold; color: ${DARK_GRAY};">后续处理流程</p>
               <p style="font-size: 14px; margin-bottom: 10px;">
                 获得批准的审稿人将被正式邀请参与同行评审。对于被拒绝的推荐，编辑团队将从平台的审稿人数据库中选择替代审稿人。
               </p>
               <p style="font-size: 14px;">
                 您可以登录您的 <strong>${PLATFORM_NAME}</strong> 账户查看稿件评审和审稿人邀请的实时状态。
               </p>
            </div>

            <div style="text-align: center; margin: 30px 0;">
              <a href="#" class="btn btn-primary" style="${BUTTON_PRIMARY}">查看稿件与审稿人状态</a>
            </div>

            <p style="font-size: 12px; color: ${LIGHT_GRAY}; text-align: center; margin-top: 10px;">
              如果按钮无法使用，请复制链接到浏览器访问：<br>
              [Manuscript Status Link]
            </p>
          </div>

          <div style="margin-top: 40px; padding-top: 20px; border-top: 1px solid #E0E0E0; text-align: center; font-size: 11px; color: ${LIGHT_GRAY};">
            <p style="margin: 5px 0;">
              如果您对审稿人推荐结果有任何疑问，请通过邮件联系编辑团队。
            </p>
            <p style="margin: 5px 0;">
              <a href="#" style="color: ${LIGHT_GRAY}; text-decoration: none;">${PLATFORM_NAME} 隐私政策链接</a>
            </p>
            <p style="margin: 5px 0;">
              &copy; 2026 ${PLATFORM_NAME}. 保留所有权利。
            </p>
          </div>

        </div>
      </body>
      </html>
    `
  }
};
