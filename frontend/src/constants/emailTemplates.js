export const PLATFORM_NAME = 'Journal Submission Platform';
export const PLATFORM_DOMAIN = 'journal-submit.com'; // Example domain
export const BRAND_RED = '#C93737';
export const DARK_GRAY = '#333333';
export const LIGHT_GRAY = '#999999';
export const BG_WHITE = '#FFFFFF';

const BASE_STYLES = `
  font-family: Arial, Helvetica, sans-serif;
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
      <span style="color: ${BRAND_RED};">${PLATFORM_NAME.charAt(0)}</span>${PLATFORM_NAME.slice(1)}
    </div>
    <div style="font-size: 12px; color: ${LIGHT_GRAY}; margin-top: 5px;">
      Journal Submission & Peer Review Platform
    </div>
  </div>
`;

const FOOTER = `
  <div style="margin-top: 40px; padding-top: 20px; border-top: 1px solid #E0E0E0; text-align: center; font-size: 11px; color: ${LIGHT_GRAY};">
    <p style="margin: 5px 0;">
      Your personal data will be processed in accordance with the <a href="#" style="color: ${BRAND_RED}; text-decoration: none;">${PLATFORM_NAME} Privacy Policy</a>.
    </p>
    <p style="margin: 5px 0;">
      &copy; 2026 ${PLATFORM_NAME}. All rights reserved.
    </p>
    <p style="margin: 5px 0;">
      If you have any questions, please contact our editorial team at: <a href="mailto:editorial@${PLATFORM_DOMAIN}" style="color: ${LIGHT_GRAY}; text-decoration: none;">editorial@${PLATFORM_DOMAIN}</a>
    </p>
  </div>
`;

export const EMAIL_TEMPLATES = {
  // Reviewer Invitation Email
  reviewerInvitation: {
    subject: `Invitation to Review Manuscript [Manuscript ID]: [Manuscript Title] - ${PLATFORM_NAME}`,
    content: `
      <!DOCTYPE html>
      <html>
      <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Invitation to Review</title>
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
              Dear Dr. [Reviewer Full Name],
            </p>
            <p style="font-size: 14px; margin-bottom: 15px;">
              We are writing on behalf of the <strong>${PLATFORM_NAME} Editorial Team</strong> to invite you to review a manuscript, which was recommended by the writers as a potential reviewer due to your expertise in [Relevant Field, e.g., cardiovascular research].
            </p>
            
            <p style="font-size: 14px; margin-bottom: 15px;">
              This invitation is extended in line with our double-blind peer review standards, and we would greatly appreciate your academic support. The key information of the manuscript and review requirements is as follows:
            </p>

            <div style="background-color: #F9F9F9; padding: 15px; border-radius: 4px; margin-bottom: 20px;">
              <p style="margin: 5px 0; font-size: 14px;"><strong>Manuscript ID:</strong> [Manuscript ID]</p>
              <p style="margin: 5px 0; font-size: 14px;"><strong>Manuscript Title:</strong> [Manuscript Title]</p>
              <p style="margin: 5px 0; font-size: 14px;"><strong>Submission Date:</strong> [Submission Date]</p>
              <p style="margin: 5px 0; font-size: 14px;"><strong>Review Type:</strong> Double-Blind Peer Review (All writer identifying information has been fully anonymized)</p>
              <p style="margin: 5px 0; font-size: 14px;"><strong>Review Due Date:</strong> [Due Date]</p>
              <p style="margin: 5px 0; font-size: 14px;"><strong>Expected Time Commitment:</strong> Approximately 2–3 hours to complete the review form and submit professional feedback</p>
            </div>

            <p style="font-size: 14px; margin-bottom: 15px;">
              Since you are not a registered reviewer on the <strong>${PLATFORM_NAME}</strong> platform, you need to complete a free and quick registration to accept the invitation and access the anonymized manuscript. Registration only requires basic academic information and takes 3–5 minutes.
            </p>
            
            <div style="text-align: center; margin: 30px 0;">
              <a href="#" class="btn btn-primary" style="${BUTTON_PRIMARY}">Accept Invitation & Register</a>
              <a href="#" class="btn btn-secondary" style="${BUTTON_SECONDARY} margin-left: 10px;">Decline Invitation</a>
            </div>

            <p style="font-size: 12px; color: ${LIGHT_GRAY}; text-align: center; margin-top: 10px;">
              If the buttons above fail to work, please copy and paste the corresponding link into your browser:<br>
              Accept: [Accept Link]<br>
              Decline: [Decline Link]
            </p>
          </div>

          <div style="margin-top: 40px; padding-top: 20px; border-top: 1px solid #E0E0E0; text-align: center; font-size: 11px; color: ${LIGHT_GRAY};">
            <p style="margin: 5px 0;">
              Your personal data will be processed in accordance with the <a href="#" style="color: ${BRAND_RED}; text-decoration: none;">${PLATFORM_NAME} Privacy Policy</a>.
            </p>
            <p style="margin: 5px 0;">
              By accepting this invitation, you confirm that you have no conflict of interest with the manuscript and agree to abide by the platform's peer review guidelines.
            </p>
            <p style="margin: 5px 0;">
              &copy; 2026 ${PLATFORM_NAME}. All rights reserved.
            </p>
            <p style="margin: 5px 0;">
              If you have any questions, please contact our editorial team at: <a href="mailto:editorial@${PLATFORM_DOMAIN}" style="color: ${LIGHT_GRAY}; text-decoration: none;">editorial@${PLATFORM_DOMAIN}</a>
            </p>
          </div>

        </div>
      </body>
      </html>
    `
  },

  // Writer Recommendation Results Notification Email
  recommendationResults: {
    subject: `Reviewer Recommendation Decision – Manuscript [Manuscript ID]: [Manuscript Title] - ${PLATFORM_NAME}`,
    content: `
      <!DOCTYPE html>
      <html>
      <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Reviewer Recommendation Results</title>
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
              Dear [Corresponding Writer Full Name],
            </p>
            <p style="font-size: 14px; margin-bottom: 15px;">
              We have completed the editorial review of the reviewers you recommended for your manuscript submitted to <strong>${PLATFORM_NAME}</strong>. The detailed decision results are as follows:
            </p>
            
            <div style="margin-bottom: 20px;">
               <p style="margin: 0 0 10px 0; font-size: 14px; font-weight: bold; color: ${DARK_GRAY}; border-bottom: 1px solid #eee; padding-bottom: 5px;">Manuscript Basic Information</p>
               <p style="margin: 5px 0; font-size: 14px;"><strong>Manuscript ID:</strong> [Manuscript ID]</p>
               <p style="margin: 5px 0; font-size: 14px;"><strong>Manuscript Title:</strong> [Manuscript Title]</p>
               <p style="margin: 5px 0; font-size: 14px;"><strong>Recommendation Submission Time:</strong> [Submission Time]</p>
            </div>

            <div style="background-color: #F9F9F9; padding: 15px; border-radius: 4px; margin-bottom: 20px;">
              <p style="margin: 0 0 15px 0; font-size: 14px; font-weight: bold; color: ${DARK_GRAY};">Reviewer Recommendation Results</p>
              
              <div style="margin-bottom: 15px; padding-bottom: 10px; border-bottom: 1px dashed #ddd;">
                <p style="margin: 0 0 5px 0; font-size: 14px; font-weight: bold;">Dr. [Reviewer Name 1]</p>
                <p style="margin: 0 0 5px 0; font-size: 14px; color: #555;">Affiliation: [Reviewer Affiliation 1]</p>
                <p style="margin: 0 0 5px 0; font-size: 14px; color: ${BRAND_RED}; font-weight: bold;">Editorial Decision: Approved</p>
                <p style="margin: 0; font-size: 14px; color: #555;">Invitation Status: Invitation has been sent on [Date]</p>
              </div>

              <div style="margin-bottom: 15px; padding-bottom: 10px; border-bottom: 1px dashed #ddd;">
                <p style="margin: 0 0 5px 0; font-size: 14px; font-weight: bold;">Dr. [Reviewer Name 2]</p>
                <p style="margin: 0 0 5px 0; font-size: 14px; color: #555;">Affiliation: [Reviewer Affiliation 2]</p>
                <p style="margin: 0 0 5px 0; font-size: 14px; color: ${BRAND_RED}; font-weight: bold;">Editorial Decision: Approved</p>
                <p style="margin: 0; font-size: 14px; color: #555;">Invitation Status: Invitation will be sent within 1 working day</p>
              </div>

              <div style="margin-bottom: 5px;">
                <p style="margin: 0 0 5px 0; font-size: 14px; font-weight: bold;">Dr. [Reviewer Name 3]</p>
                <p style="margin: 0 0 5px 0; font-size: 14px; color: #555;">Affiliation: [Reviewer Affiliation 3]</p>
                <p style="margin: 0 0 5px 0; font-size: 14px; color: #999; font-weight: bold;">Editorial Decision: Rejected</p>
                <p style="margin: 0; font-size: 14px; color: #555;">Rejection Reason: [Objective reason, e.g., potential conflict of interest, research field mismatch]</p>
              </div>
            </div>

            <div style="margin-bottom: 20px;">
               <p style="margin: 0 0 10px 0; font-size: 14px; font-weight: bold; color: ${DARK_GRAY};">Next Processing Flow</p>
               <p style="font-size: 14px; margin-bottom: 10px;">
                 Approved reviewers will be officially invited to participate in the peer review. For rejected recommendations, the editorial team will select alternative reviewers from the platform's reviewer database.
               </p>
               <p style="font-size: 14px;">
                 You can log in to your <strong>${PLATFORM_NAME}</strong> account to view the real-time status of manuscript review and reviewer invitations.
               </p>
            </div>

            <div style="text-align: center; margin: 30px 0;">
              <a href="#" class="btn btn-primary" style="${BUTTON_PRIMARY}">View Manuscript & Reviewer Status</a>
            </div>

            <p style="font-size: 12px; color: ${LIGHT_GRAY}; text-align: center; margin-top: 10px;">
              If the button is unavailable, please copy the link to your browser for access:<br>
              [Manuscript Status Link]
            </p>
          </div>

          <div style="margin-top: 40px; padding-top: 20px; border-top: 1px solid #E0E0E0; text-align: center; font-size: 11px; color: ${LIGHT_GRAY};">
            <p style="margin: 5px 0;">
              If you have any questions about the reviewer recommendation results, please contact the editorial team via email.
            </p>
            <p style="margin: 5px 0;">
              <a href="#" style="color: ${LIGHT_GRAY}; text-decoration: none;">${PLATFORM_NAME} Privacy Policy Link</a>
            </p>
            <p style="margin: 5px 0;">
              &copy; 2026 ${PLATFORM_NAME}. All rights reserved.
            </p>
          </div>

        </div>
      </body>
      </html>
    `
  }
};
