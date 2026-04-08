# User Acceptance Test (UAT) - Merit System

## Overview

This UAT document validates core user-facing features of the Merit system, including navigation, user authentication, event management, rewards, and visual feedback mechanisms.

---

## 1. Navigation & Navbar Functionality

### Test Case: Navbar Hamburger Menu Expansion (Student)

| **Category** | **Details** |
|---|---|
| **Test case** | TC-NAV-001: Hamburger menu toggle opens and closes sidebar navigation |
| **Prerequisites** | Student user is logged into the system; browser is at mobile viewport width (< 768px) or desktop; Merit logo is visible in navbar |
| **Test Steps** | 1. Observe the navbar at the top of the page<br>2. Click the hamburger menu icon (☰) on the left side<br>3. Verify the sidebar drawer slides in from the left<br>4. Click the hamburger icon again or click the overlay<br>5. Verify the sidebar drawer slides out and closes |
| **Test Criteria** | ✓ Hamburger icon is visible<br>✓ Sidebar drawer appears with smooth animation<br>✓ Sidebar contains all expected student menu links (Events, Leaderboard, Scan QR, Profile, Rewards, Badges, About Us)<br>✓ Drawer closes when toggled or overlay is clicked<br>✓ Page content remains accessible and not blocked |

### Test Case: Navbar Menu Links Navigation

| **Category** | **Details** |
|---|---|
| **Test case** | TC-NAV-002: Navbar menu links navigate to correct pages |
| **Prerequisites** | User is logged in; Student or Staff role; sidebar is open (if on mobile) |
| **Test Steps** | 1. For Student users: Click on "Events" link in navbar/drawer<br>2. Verify page loads and displays student events<br>3. Click on "Leaderboard" link<br>4. Verify leaderboard page loads with ranking data<br>5. Click on "Profile" link<br>6. Verify profile page displays user information<br>7. For Staff users: Click on "Events", "Rewards", "Flagged", "Appeals" links<br>8. Verify each page loads correctly |
| **Test Criteria** | ✓ All links navigate to correct pages<br>✓ Active menu item is highlighted with purple background (#660c9e)<br>✓ Page title updates appropriately<br>✓ No 404 errors occur<br>✓ Content loads within 2 seconds |

### Test Case: Navbar Active Link Indication

| **Category** | **Details** |
|---|---|
| **Test case** | TC-NAV-003: Active menu item is visually highlighted |
| **Prerequisites** | User is logged in on any page with navigation menu |
| **Test Steps** | 1. Navigate to the Events page<br>2. Check the sidebar menu - "Events" should be highlighted<br>3. Navigate to Leaderboard page<br>4. Check the sidebar menu - "Leaderboard" should be highlighted (Events is no longer highlighted)<br>5. Navigate to Rewards page<br>6. Check the sidebar menu - "Rewards" should be highlighted |
| **Test Criteria** | ✓ Only the current page's menu item is highlighted<br>✓ Highlight color is purple (#660c9e)<br>✓ Highlight changes when navigating between pages<br>✓ Highlight is applied consistently across all menu items |

### Test Case: Logout Functionality

| **Category** | **Details** |
|---|---|
| **Test case** | TC-NAV-004: Logout button ends user session |
| **Prerequisites** | User is logged into the system |
| **Test Steps** | 1. Locate the "Logout" button in the top navbar (visible on all pages)<br>2. Click the "Logout" button<br>3. Verify redirect to login or home page<br>4. Attempt to navigate back to a protected page using browser back button<br>5. Verify session is terminated and user is redirected to login |
| **Test Criteria** | ✓ Logout button is visible and clickable<br>✓ User is logged out immediately<br>✓ Session is invalidated (cannot access protected pages)<br>✓ User is redirected to login/home page<br>✓ All stored session tokens are cleared |

---

## 2. Authentication & Login

### Test Case: User Login - Valid Credentials

| **Category** | **Details** |
|---|---|
| **Test case** | TC-AUTH-001: User can log in with valid username and password |
| **Prerequisites** | User account exists in system; not currently logged in; browser at login page |
| **Test Steps** | 1. Navigate to login page<br>2. Enter valid username in "Username" field<br>3. Enter correct password in "Password" field<br>4. Click "Login" button<br>5. Verify redirect to appropriate dashboard (Student/Staff based on role) |
| **Test Criteria** | ✓ Login form accepts input<br>✓ Login button is clickable<br>✓ User is authenticated and logged in<br>✓ Redirect occurs to correct dashboard within 2 seconds<br>✓ Navbar displays user's role-specific menu items<br>✓ No error messages appear |

### Test Case: User Login - Invalid Credentials

| **Category** | **Details** |
|---|---|
| **Test case** | TC-AUTH-002: User cannot log in with invalid credentials; error message displayed |
| **Prerequisites** | Not logged in; browser at login page |
| **Test Steps** | 1. Navigate to login page<br>2. Enter valid username<br>3. Enter incorrect password<br>4. Click "Login" button<br>5. Observe error notification<br>6. Repeat steps 2-5 with invalid username |
| **Test Criteria** | ✓ Login fails with invalid credentials<br>✓ Clear error message appears (e.g., "Invalid username or password")<br>✓ Error message is visible and readable<br>✓ User remains on login page<br>✓ User can retry login |

### Test Case: Signup New User

| **Category** | **Details** |
|---|---|
| **Test case** | TC-AUTH-003: New user can sign up with valid information |
| **Prerequisites** | Not logged in; signup page is accessible; new username does not exist |
| **Test Steps** | 1. Navigate to signup page<br>2. Enter new username<br>3. Enter email address<br>4. Enter password (should meet strength requirements)<br>5. Enter password confirmation<br>6. Click "Sign Up" button<br>7. Verify account is created and user is logged in or redirected to login |
| **Test Criteria** | ✓ Signup form accepts input<br>✓ Form validates password strength<br>✓ Account is created successfully<br>✓ Success message appears (e.g., "Account created successfully")<br>✓ User can log in with new credentials<br>✓ No duplicate accounts are created |

---

## 3. Flash Notifications & Visual Feedback

### Test Case: Flash Message Display & Auto-Dismiss

| **Category** | **Details** |
|---|---|
| **Test case** | TC-FEEDBACK-001: Flash messages appear and automatically dismiss after timeout |
| **Prerequisites** | User is logged in; perform an action that triggers a flash message (e.g., login, event join) |
| **Test Steps** | 1. Perform action that generates a flash message (join event, redeem reward, etc.)<br>2. Observe notification appears in top-right corner<br>3. Note the notification styling (color, text clarity)<br>4. Wait 3 seconds without clicking<br>5. Verify notification fades out and disappears<br>6. Verify page content is not blocked by message |
| **Test Criteria** | ✓ Flash message appears immediately after action<br>✓ Message is positioned in top-right corner<br>✓ Message text is clear and readable<br>✓ Message color indicates category (success=green, error=red, info=blue)<br>✓ Message auto-dismisses after 3 seconds<br>✓ Message can be manually closed with close button (×)<br>✓ Multiple messages stack vertically<br>✓ Page content remains accessible |

### Test Case: Flash Message Manual Dismiss

| **Category** | **Details** |
|---|---|
| **Test case** | TC-FEEDBACK-002: User can manually close flash notifications |
| **Prerequisites** | Flash message is visible on page |
| **Test Steps** | 1. Locate flash message in top-right corner<br>2. Click the close button (×) on the message<br>3. Verify message disappears immediately<br>4. Verify page layout adjusts properly after dismissal |
| **Test Criteria** | ✓ Close button is visible and clickable<br>✓ Message disappears on click<br>✓ No animation glitches occur<br>✓ Other messages (if present) remain unaffected |

### Test Case: Error Notification Display

| **Category** | **Details** |
|---|---|
| **Test case** | TC-FEEDBACK-003: Error messages display with appropriate styling and content |
| **Prerequisites** | Perform action that triggers error (insufficient permissions, validation failure, etc.) |
| **Test Steps** | 1. Attempt action that results in error (e.g., redeem unavailable reward, leave event without joining)<br>2. Observe error notification appears<br>3. Verify error message clearly describes the problem<br>4. Verify error styling is distinct (red color)<br>5. Verify user can retry or proceed with alternative action |
| **Test Criteria** | ✓ Error message appears prominently<br>✓ Error message text is descriptive and actionable<br>✓ Error styling is clearly distinct from success/info messages<br>✓ No sensitive information is exposed in error messages<br>✓ User can dismiss error and continue |

### Test Case: Success Notification Display

| **Category** | **Details** |
|---|---|
| **Test case** | TC-FEEDBACK-004: Success messages display with appropriate styling |
| **Prerequisites** | Perform action that completes successfully (join event, redeem reward, create event, etc.) |
| **Test Steps** | 1. Perform successful action<br>2. Observe success notification appears<br>3. Verify success message confirms the action completed<br>4. Verify success styling is distinct (green color)<br>5. Verify notification auto-dismisses or has close button |
| **Test Criteria** | ✓ Success message appears immediately<br>✓ Message confirms action was completed<br>✓ Green/success color is used consistently<br>✓ Message text is clear and specific<br>✓ Message follows same auto-dismiss pattern as other notifications |

---

## 4. Student Dashboard & Events

### Test Case: Student View Upcoming Events

| **Category** | **Details** |
|---|---|
| **Test case** | TC-EVENTS-001: Student can view list of upcoming events with details |
| **Prerequisites** | Logged in as student; upcoming events exist in system |
| **Test Steps** | 1. Click on "Events" in navbar<br>2. Observe events list page loads<br>3. Verify each event card displays: event name, date/time, description, type<br>4. Verify events are sorted by date (earliest first)<br>5. Click on an event to view full details<br>6. Verify event detail modal/page shows all information |
| **Test Criteria** | ✓ Events page loads without errors<br>✓ Event cards are displayed in list view<br>✓ Each card shows key information clearly<br>✓ Events are chronologically ordered<br>✓ Event detail view is accessible<br>✓ Page is responsive on mobile and desktop |

### Test Case: Student Join Event

| **Category** | **Details** |
|---|---|
| **Test case** | TC-EVENTS-002: Student can join an event |
| **Prerequisites** | Logged in as student; viewing events page; an available event exists that student has not joined |
| **Test Steps** | 1. Navigate to Events page<br>2. Find an event not yet joined<br>3. Click "Join" or "Register" button on event<br>4. Verify join button changes or indicates "Joined"<br>5. Verify success message appears<br>6. Navigate to Profile or My Events to confirm enrollment |
| **Test Criteria** | ✓ Join button is visible and clickable<br>✓ Join action completes without errors<br>✓ Success message confirms enrollment<br>✓ Event now appears in student's event list<br>✓ Join button is disabled or shows "Joined" status<br>✓ Student count for event increases |

### Test Case: Student Leave Event

| **Category** | **Details** |
|---|---|
| **Test case** | TC-EVENTS-003: Student can leave a joined event |
| **Prerequisites** | Logged in as student; student is enrolled in at least one event |
| **Test Steps** | 1. Navigate to Events page or My Events<br>2. Find an event the student has joined<br>3. Click "Leave" or "Withdraw" button<br>4. Confirm withdrawal if prompted<br>5. Verify leave button is replaced or disabled<br>6. Verify success message appears |
| **Test Criteria** | ✓ Leave button is visible for joined events<br>✓ Confirmation prompt appears (optional but recommended)<br>✓ Leave action completes successfully<br>✓ Success message confirms withdrawal<br>✓ Event is removed from student's event list<br>✓ Attendance record is removed |

---

## 5. Rewards & Redemption

### Test Case: Student View Available Rewards

| **Category** | **Details** |
|---|---|
| **Test case** | TC-REWARDS-001: Student can view list of available rewards |
| **Prerequisites** | Logged in as student; rewards exist in system; student has sufficient merit points or credits |
| **Test Steps** | 1. Click on "Rewards" in navbar<br>2. Observe rewards page loads<br>3. Verify reward cards are displayed with: reward name, description, cost/points, availability status<br>4. Verify available rewards are distinguishable from unavailable ones<br>5. Scroll through list to verify all rewards load properly |
| **Test Criteria** | ✓ Rewards page loads without errors<br>✓ Reward cards display clearly with readable text<br>✓ Reward cost/point value is visible<br>✓ Available/unavailable status is clear<br>✓ Page is responsive on mobile and desktop<br>✓ Rewards can be searched or filtered (if implemented) |

### Test Case: Student Redeem Available Reward

| **Category** | **Details** |
|---|---|
| **Test case** | TC-REWARDS-002: Student can redeem an available reward with sufficient balance |
| **Prerequisites** | Logged in as student; viewing rewards page; student has sufficient points/balance; reward is available |
| **Test Steps** | 1. Navigate to Rewards page<br>2. Select an available reward with sufficient points<br>3. Click "Redeem" button<br>4. Verify confirmation dialog appears with reward and cost details<br>5. Click "Confirm" to redeem<br>6. Verify success message and reward status changes<br>7. Verify student point balance decreases by reward cost |
| **Test Criteria** | ✓ Redeem button is visible and clickable<br>✓ Confirmation dialog is clear and informative<br>✓ Redemption completes successfully<br>✓ Success message confirms redemption with reward details<br>✓ Reward status changes to "Redeemed" or "Claimed"<br>✓ Student balance updates immediately<br>✓ Redeemed reward appears in redemption history |

### Test Case: Student Cannot Redeem Reward with Insufficient Balance

| **Category** | **Details** |
|---|---|
| **Test case** | TC-REWARDS-003: System prevents redeeming reward with insufficient points |
| **Prerequisites** | Logged in as student; student has insufficient points/balance for a reward |
| **Test Steps** | 1. Navigate to Rewards page<br>2. Find a reward with cost higher than student's current balance<br>3. Verify Redeem button is disabled or shows "Insufficient Balance"<br>4. Attempt to click disabled Redeem button<br>5. Verify no action occurs or error message appears |
| **Test Criteria** | ✓ Redeem button is disabled for unaffordable rewards<br>✓ Disabled state is visually clear<br>✓ Hover tooltip explains why button is disabled (optional)<br>✓ No error occurs if button is clicked<br>✓ Student balance remains unchanged<br>✓ Current balance is displayed clearly |

---

## 6. Badges & Achievements

### Test Case: Student View Earned Badges

| **Category** | **Details** |
|---|---|
| **Test case** | TC-BADGES-001: Student can view earned badges with details |
| **Prerequisites** | Logged in as student; student has earned at least one badge |
| **Test Steps** | 1. Click on "Badges" in navbar<br>2. Observe badges page/section loads<br>3. Verify earned badges are displayed prominently<br>4. Verify each badge shows: badge name, description, date earned<br>5. Verify badge icons/images display correctly<br>6. Click on a badge to view additional details (if available) |
| **Test Criteria** | ✓ Badges page loads without errors<br>✓ Earned badges are displayed and visually distinct<br>✓ Badge information is complete and accurate<br>✓ Badge icons/images load and display correctly<br>✓ Badges are organized logically (by category, date, etc.)<br>✓ Page is responsive on mobile and desktop |

### Test Case: Horizontal Scroll for Earned Badges

| **Category** | **Details** |
|---|---|
| **Test case** | TC-BADGES-002: Earned badges can be scrolled horizontally when exceeding viewport |
| **Prerequisites** | Logged in as student; student has multiple earned badges; "earned-scroll" container is visible |
| **Test Steps** | 1. Navigate to a page displaying earned badges (e.g., Profile or Badges page)<br>2. Verify horizontal scrollbar is visible at bottom of badge container<br>3. Use mouse to drag scrollbar horizontally<br>4. Verify badges scroll smoothly to the right<br>5. Verify additional badges become visible<br>6. Scroll left to see previously hidden badges<br>7. Test on touch device by swiping horizontally |
| **Test Criteria** | ✓ Horizontal scrollbar is always visible (stable gutter)<br>✓ Scrollbar is accessible and responsive<br>✓ Badges scroll smoothly without lag<br>✓ All earned badges are accessible via scrolling<br>✓ Scrollbar styling matches app theme<br>✓ Touch/swipe scrolling works on mobile devices<br>✓ Scrollbar thumb changes color on hover |

---

## 7. Leaderboard & Progress

### Test Case: Student View Leaderboard

| **Category** | **Details** |
|---|---|
| **Test case** | TC-LEADERBOARD-001: Student can view ranked leaderboard of all students |
| **Prerequisites** | Logged in as student; multiple students exist in system with merit points |
| **Test Steps** | 1. Click on "Leaderboard" in navbar<br>2. Observe leaderboard page loads<br>3. Verify students are ranked by points (highest first)<br>4. Verify each entry shows: rank, student name, total points, badges count<br>5. Identify current user's position on leaderboard<br>6. Verify ranking is accurate and up-to-date |
| **Test Criteria** | ✓ Leaderboard page loads without errors<br>✓ Students are correctly ranked by points (descending)<br>✓ Current user is highlighted or clearly indicated<br>✓ All required columns are visible and readable<br>✓ Ranking updates when points change<br>✓ Page is responsive on mobile and desktop |

### Test Case: Student View Personal Progress

| **Category** | **Details** |
|---|---|
| **Test case** | TC-PROGRESS-001: Student can view personal progress and achievement metrics |
| **Prerequisites** | Logged in as student; student has activity history (events, rewards, badges) |
| **Test Steps** | 1. Click on "Profile" in navbar<br>2. Observe profile page loads<br>3. Verify personal statistics display: total points, events attended, badges earned, rewards redeemed<br>4. Verify progress indicators (if any) show visual representation of achievements<br>5. Verify event history shows past and upcoming events<br>6. Verify reward redemption history is available |
| **Test Criteria** | ✓ Profile page loads without errors<br>✓ All personal statistics are displayed and accurate<br>✓ Event history is complete and chronological<br>✓ Reward history shows date of redemption<br>✓ Profile information is current<br>✓ Page layout is clear and organized |

---

## 8. QR Code Scanning

### Test Case: Student Access QR Scan Page

| **Category** | **Details** |
|---|---|
| **Test case** | TC-QR-001: Student can access QR code scanning page |
| **Prerequisites** | Logged in as student; device has camera/browser supports camera access |
| **Test Steps** | 1. Click on "Scan QR" in navbar<br>2. Observe QR scan page loads<br>3. Verify camera permission request appears (if first time)<br>4. Grant camera permissions if prompted<br>5. Verify camera feed displays in video element<br>6. Verify scanner interface is user-friendly with instructions |
| **Test Criteria** | ✓ QR scan page loads without errors<br>✓ Camera permission dialog appears (if needed)<br>✓ Camera feed displays when permission granted<br>✓ Instructions are clear for user<br>✓ Interface is responsive and accessible<br>✓ No console errors appear |

### Test Case: Student Scan Valid QR Code

| **Category** | **Details** |
|---|---|
| **Test case** | TC-QR-002: Student can scan QR code to check in to event |
| **Prerequisites** | Logged in as student; QR scan page is open; valid QR code is available; student is registered for corresponding event |
| **Test Steps** | 1. Navigate to Scan QR page<br>2. Position valid QR code in front of camera<br>3. Wait for code to be detected and scanned<br>4. Verify success notification appears with event name<br>5. Verify attendance is recorded in event history<br>6. Attempt to scan same code again<br>7. Verify system handles duplicate scan appropriately |
| **Test Criteria** | ✓ QR code is detected and scanned<br>✓ Success message confirms check-in to correct event<br>✓ Attendance is recorded in student's history<br>✓ Student receives confirmation feedback<br>✓ Duplicate scans are handled (error or already checked in message)<br>✓ No scanning errors occur |

---

## 9. Staff Dashboard - Events Management

### Test Case: Staff Create New Event

| **Category** | **Details** |
|---|---|
| **Test case** | TC-STAFF-EVENTS-001: Staff can create a new event with required details |
| **Prerequisites** | Logged in as staff; Events page is accessible |
| **Test Steps** | 1. Navigate to Events page (staff version)<br>2. Click "Create Event" or "New Event" button<br>3. Fill in event form: name, description, type, start date, end date, location (if applicable)<br>4. Click "Create" button<br>5. Verify event is created and appears in event list<br>6. Verify success message confirms creation<br>7. Verify event details are correct |
| **Test Criteria** | ✓ Event creation form is accessible<br>✓ Form accepts all required inputs<br>✓ Form validation works for required fields<br>✓ Event is successfully created and saved<br>✓ Success message confirms creation<br>✓ New event is visible in event list immediately<br>✓ Event can be edited after creation |

### Test Case: Staff Generate QR Code for Event

| **Category** | **Details** |
|---|---|
| **Test case** | TC-STAFF-EVENTS-002: Staff can generate QR code for event attendance tracking |
| **Prerequisites** | Logged in as staff; event is created and viewable |
| **Test Steps** | 1. Navigate to an event in staff Events page<br>2. Locate QR code generation option (button or link)<br>3. Click to generate QR code<br>4. Verify QR code displays on page<br>5. Click to download or print QR code<br>6. Test QR code by scanning with student device |
| **Test Criteria** | ✓ QR code generation option is accessible<br>✓ QR code is generated and displays correctly<br>✓ QR code is scannable with standard QR readers<br>✓ QR code contains correct event identifier<br>✓ Download/print functionality works<br>✓ Visual feedback confirms generation |

---

## 10. Staff Dashboard - Rewards Management

### Test Case: Staff Create New Reward

| **Category** | **Details** |
|---|---|
| **Test case** | TC-STAFF-REWARDS-001: Staff can create and configure new reward offerings |
| **Prerequisites** | Logged in as staff; Rewards page is accessible |
| **Test Steps** | 1. Navigate to Rewards page (staff version)<br>2. Click "Create Reward" or "New Reward" button<br>3. Fill in reward details: name, description, cost/point value, quantity available<br>4. Set availability dates (optional)<br>5. Click "Create" button<br>6. Verify reward appears in rewards list<br>7. Verify success message confirms creation |
| **Test Criteria** | ✓ Reward creation form is accessible<br>✓ All fields accept input correctly<br>✓ Form validation enforces required fields<br>✓ Reward is successfully created<br>✓ Success message confirms creation<br>✓ New reward is visible in list<br>✓ Reward settings are saved correctly |

### Test Case: Staff Toggle Reward Availability

| **Category** | **Details** |
|---|---|
| **Test case** | TC-STAFF-REWARDS-002: Staff can enable/disable reward availability to students |
| **Prerequisites** | Logged in as staff; at least one reward exists; Rewards page is accessible |
| **Test Steps** | 1. Navigate to Rewards page<br>2. Find an active reward in the list<br>3. Click on reward to view details<br>4. Locate "Toggle Availability" or "Disable" option<br>5. Click to toggle reward status<br>6. Verify visual indication changes (status, button label)<br>7. Log in as student and verify reward is unavailable<br>8. Return to staff view and re-enable reward |
| **Test Criteria** | ✓ Toggle option is accessible and clear<br>✓ Reward status changes immediately<br>✓ Visual indicator updates (color, text, button state)<br>✓ Students cannot see disabled rewards<br>✓ Students can see re-enabled rewards<br>✓ Status change triggers success message |

---

## 11. Responsive Design & Layout

### Test Case: Mobile Responsive Layout - Navbar

| **Category** | **Details** |
|---|---|
| **Test case** | TC-RESPONSIVE-001: Navbar is fully functional on mobile devices |
| **Prerequisites** | Access site on mobile device (< 768px width) or browser in mobile viewport; any page |
| **Test Steps** | 1. View site at mobile width (e.g., 375px)<br>2. Verify hamburger menu is visible for students (always) and staff (at small screens)<br>3. Verify "Merit" logo is visible and centered<br>4. Verify Logout button is accessible<br>5. Verify main navigation menu items are hidden in drawer<br>6. Click hamburger to open drawer<br>7. Verify drawer menu is fully accessible and readable |
| **Test Criteria** | ✓ Hamburger menu is visible at mobile width<br>✓ Logo is visible and properly sized<br>✓ Logout button is accessible<br>✓ Drawer opens and closes properly<br>✓ All menu items are readable and tappable<br>✓ Navbar does not overflow or cause horizontal scroll<br>✓ Touch interactions work smoothly |

### Test Case: Mobile Responsive Layout - Content

| **Category** | **Details** |
|---|---|
| **Test case** | TC-RESPONSIVE-002: Page content is readable and usable on mobile |
| **Prerequisites** | Access site on mobile device (< 768px width) or browser in mobile viewport |
| **Test Steps** | 1. Navigate to Events page on mobile<br>2. Verify event cards stack vertically (single column)<br>3. Verify text is readable without zooming<br>4. Verify buttons are large enough to tap (minimum 44x44px)<br>5. Verify tables and lists don't exceed width<br>6. Scroll through page to verify no horizontal overflow<br>7. Repeat on other pages (Rewards, Profile, Leaderboard) |
| **Test Criteria** | ✓ Content stacks properly at mobile width<br>✓ Text is readable (no 12pt or smaller)<br>✓ Buttons and inputs are tap-friendly (44x44px minimum)<br>✓ No horizontal scrolling required<br>✓ Images scale responsively<br>✓ Tables are scrollable or reorganized for mobile<br>✓ Page loads and functions smoothly |

### Test Case: Tablet & Desktop Layout

| **Category** | **Details** |
|---|---|
| **Test case** | TC-RESPONSIVE-003: Page layout adapts for tablet and desktop viewports |
| **Prerequisites** | Access site on tablet (768px-1024px) and desktop (>1024px) |
| **Test Steps** | 1. View site at tablet width (e.g., 768px)<br>2. Verify menu items are visible in navbar (if space permits)<br>3. Verify content uses available width efficiently<br>4. View site at desktop width (e.g., 1400px)<br>5. Verify layout is centered and max-width is respected<br>6. Verify sidebar menu can be collapsed/expanded on staff view<br>7. Verify no excessive whitespace or compressed content |
| **Test Criteria** | ✓ Menu adapts to available width<br>✓ Content is centered with proper max-width<br>✓ Padding and margins are appropriate<br>✓ Text is readable and comfortable<br>✓ Layout is symmetrical and professional-looking<br>✓ No content is hidden or broken on any viewport<br>✓ Images and icons scale appropriately |

---

## 12. Performance & Loading

### Test Case: Page Load Time

| **Category** | **Details** |
|---|---|
| **Test case** | TC-PERF-001: Pages load in acceptable time (< 3 seconds) |
| **Prerequisites** | Standard internet connection; network dev tools available |
| **Test Steps** | 1. Open browser developer tools (F12)<br>2. Go to Network tab<br>3. Navigate to Events page and wait for full load<br>4. Note total load time (shown in status bar)<br>5. Repeat for other pages: Leaderboard, Rewards, Profile<br>6. Test with cache cleared (Ctrl+Shift+Delete) |
| **Test Criteria** | ✓ Page loads within 3 seconds on standard connection<br>✓ Critical content (navbar, main content) loads first<br>✓ No console errors appear during load<br>✓ Images load without breaking layout (lazy loaded or sized)<br>✓ No unoptimized resources (oversized images, unused CSS/JS)<br>✓ Subsequent page navigations are faster (caching works) |

---

## 13. Accessibility

### Test Case: Keyboard Navigation

| **Category** | **Details** |
|---|---|
| **Test case** | TC-A11Y-001: All interactive elements are accessible via keyboard |
| **Prerequisites** | Any page with interactive elements; keyboard available |
| **Test Steps** | 1. Press Tab key repeatedly to navigate through page elements<br>2. Verify focus indicator is visible on each element<br>3. Press Enter or Space to activate buttons/links<br>4. Verify modal dialogs can be opened and closed with keyboard<br>5. Press Escape to close modals and drawers<br>6. Test form submission with Enter key |
| **Test Criteria** | ✓ All buttons and links are focusable via Tab<br>✓ Focus indicator is visible and clear<br>✓ Buttons activate with Enter/Space<br>✓ Links navigate with Enter<br>✓ Modals can be closed with Escape<br>✓ Form can be submitted with Enter<br>✓ Tab order is logical and follows visual flow |

### Test Case: Color Contrast

| **Category** | **Details** |
|---|---|
| **Test case** | TC-A11Y-002: Text has sufficient color contrast for readability |
| **Prerequisites** | Any page; color contrast checker tool available (optional) |
| **Test Steps** | 1. Navigate to main pages (Events, Rewards, Profile)<br>2. Verify text on navbar is readable (white text on purple #660c9e)<br>3. Verify body text is readable (dark text on light background)<br>4. Verify link colors are distinct from regular text<br>5. Verify error messages are red and readable<br>6. Use color contrast checker to verify WCAG AA compliance |
| **Test Criteria** | ✓ Normal text has 4.5:1 contrast ratio (WCAG AA)<br>✓ Large text (18pt+) has 3:1 contrast ratio<br>✓ Links are visually distinct from regular text<br>✓ Color is not the only indicator (icons or text also used)<br>✓ All text is readable without color dependency<br>✓ Focus indicators have sufficient contrast |

---

## 14. Error Handling & Edge Cases

### Test Case: 404 Page Not Found

| **Category** | **Details** |
|---|---|
| **Test case** | TC-ERROR-001: Accessing invalid URL displays helpful 404 error page |
| **Prerequisites** | Not logged in or logged in; internet connection active |
| **Test Steps** | 1. Navigate to non-existent page (e.g., /invalid-page)<br>2. Observe error page displays<br>3. Verify page explains "Page Not Found" or similar message<br>4. Verify link to home or previous page is available<br>5. Verify navbar is still visible and functional |
| **Test Criteria** | ✓ 404 page is displayed instead of blank screen<br>✓ Error message is clear and user-friendly<br>✓ Navigation options are provided<br>✓ Navbar is functional and accessible<br>✓ No console errors appear |

### Test Case: Unauthorized Access Attempt

| **Category** | **Details** |
|---|---|
| **Test case** | TC-ERROR-002: Attempting to access protected pages without login redirects appropriately |
| **Prerequisites** | Not logged in |
| **Test Steps** | 1. Open dev console and copy URL of a protected page (e.g., /events)<br>2. Logout if currently logged in<br>3. Navigate to protected URL directly<br>4. Verify redirect to login page occurs<br>5. Verify helpful message appears (optional)<br>6. Verify navbar shows guest version |
| **Test Criteria** | ✓ Access is denied to protected pages<br>✓ User is redirected to login page<br>✓ Original page context is preserved (optional redirect after login)<br>✓ No sensitive information is leaked<br>✓ Error is handled gracefully |

### Test Case: Network Error Handling

| **Category** | **Details** |
|---|---|
| **Test case** | TC-ERROR-003: Application handles network errors gracefully |
| **Prerequisites** | Network dev tools available (to simulate network failure) |
| **Test Steps** | 1. Open page and throttle network to "Offline" in dev tools<br>2. Attempt to load new page or submit form<br>3. Observe error message or fallback UI appears<br>4. Restore network and refresh page<br>5. Verify page loads normally<br>6. Verify offline state is handled gracefully (not frozen) |
| **Test Criteria** | ✓ Network errors are caught and communicated<br>✓ User is not left with blank screen or frozen UI<br>✓ Clear message explains connection issue<br>✓ Retry mechanism is available<br>✓ No sensitive error data is exposed<br>✓ App recovers when network is restored |

---

## 15. Cross-Browser Compatibility

### Test Case: Compatibility - Chrome/Edge

| **Category** | **Details** |
|---|---|
| **Test case** | TC-COMPAT-001: Application functions correctly in Chrome and Edge browsers |
| **Prerequisites** | Chrome (latest) and Edge (latest) are installed |
| **Test Steps** | 1. Open app in Chrome and verify: navbar, hamburger menu, navigation, flash messages<br>2. Complete user flow: login → view events → join event → view rewards<br>3. Open app in Edge and repeat same user flow<br>4. Verify visual styling is consistent (colors, fonts, spacing)<br>5. Verify no console errors in either browser |
| **Test Criteria** | ✓ All features work identically in Chrome and Edge<br>✓ Visual styling is consistent<br>✓ No browser-specific bugs or issues<br>✓ Flash messages work in both browsers<br>✓ Navigation is smooth in both browsers<br>✓ No console errors |

### Test Case: Compatibility - Firefox & Safari

| **Category** | **Details** |
|---|---|
| **Test case** | TC-COMPAT-002: Application functions correctly in Firefox and Safari browsers |
| **Prerequisites** | Firefox (latest) and Safari (latest) are installed |
| **Test Steps** | 1. Open app in Firefox and verify navbar, hamburger, and navigation work<br>2. Complete user flow in Firefox<br>3. Open app in Safari (macOS/iOS) and repeat user flow<br>4. Verify CSS styling is consistent across browsers<br>5. Test camera QR scanning in Safari (if applicable)<br>6. Verify no console errors in either browser |
| **Test Criteria** | ✓ All features work in Firefox and Safari<br>✓ Visual styling is consistent across browsers<br>✓ No browser-specific issues or bugs<br>✓ Camera permissions work in Safari<br>✓ No console errors<br>✓ Responsive layout works correctly |

---

## 16. Data Validation & Security

### Test Case: Form Input Validation

| **Category** | **Details** |
|---|---|
| **Test case** | TC-VALIDATE-001: Form inputs are validated before submission |
| **Prerequisites** | Any form is accessible (login, signup, event creation, etc.) |
| **Test Steps** | 1. Attempt to submit login form with empty username<br>2. Verify error message appears (required field)<br>3. Enter username but leave password empty<br>4. Attempt to submit and verify error<br>5. Enter invalid email in signup form<br>6. Verify email format error message<br>7. Try to create event without required fields |
| **Test Criteria** | ✓ Required field errors display<br>✓ Format validation works (email, URL, etc.)<br>✓ Error messages are clear and specific<br>✓ Form is not submitted with invalid data<br>✓ Errors are displayed near the problematic field<br>✓ User can correct and resubmit |

### Test Case: Password Strength Requirements

| **Category** | **Details** |
|---|---|
| **Test case** | TC-VALIDATE-002: Password must meet minimum strength requirements |
| **Prerequisites** | Signup page or change password page is accessible |
| **Test Steps** | 1. Navigate to signup or password change<br>2. Enter weak password (e.g., "123" or "password")<br>3. Verify strength validation message appears<br>4. Try password that meets requirements (8+ chars, mixed case, number, symbol)<br>5. Verify password is accepted<br>6. Verify password confirmation matches before submission |
| **Test Criteria** | ✓ Password strength requirements are enforced<br>✓ Requirements are clearly communicated<br>✓ Weak passwords are rejected with message<br>✓ Strong passwords are accepted<br>✓ Password field has confirmation match validation<br>✓ Mismatch is caught before submission |

### Test Case: XSS Protection

| **Category** | **Details** |
|---|---|
| **Test case** | TC-SECURITY-001: HTML/script injection is prevented |
| **Prerequisites** | Any form that accepts user input is accessible |
| **Test Steps** | 1. Try to submit form with script tag in input: <script>alert('XSS')</script><br>2. Verify script is not executed on page<br>3. Check if malicious input is sanitized or escaped in output<br>4. Try other XSS vectors (img onerror, etc.)<br>5. Verify none are executed |
| **Test Criteria** | ✓ Scripts are not executed<br>✓ Input is properly escaped or sanitized<br>✓ No JavaScript injection is possible via forms<br>✓ No pop-ups or alerts from injected code<br>✓ Content is displayed safely (as text, not HTML) |

---

## 17. Modals & Dialogs

### Test Case: Modal Dialog Opens and Closes

| **Category** | **Details** |
|---|---|
| **Test case** | TC-MODAL-001: Modal dialogs open, close, and handle user interactions |
| **Prerequisites** | Perform action that opens modal (join event, redeem reward, confirm action) |
| **Test Steps** | 1. Click action that triggers modal (join event, edit, delete confirmation)<br>2. Verify modal appears centered on page<br>3. Verify modal has clear title and description<br>4. Verify action buttons (Confirm/Cancel) are visible<br>5. Click Cancel and verify modal closes without action<br>6. Open modal again and click Confirm<br>7. Verify modal closes and action executes<br>8. Press Escape key to close modal |
| **Test Criteria** | ✓ Modal appears with overlay<br>✓ Modal is centered and readable<br>✓ Cancel button closes without action<br>✓ Confirm button executes action and closes<br>✓ Escape key closes modal<br>✓ Overlay outside modal can close it (optional)<br>✓ Page content is not accessible while modal is open |

### Test Case: Modal Does Not Lose Focus

| **Category** | **Details** |
|---|---|
| **Test case** | TC-MODAL-002: Keyboard focus is trapped within modal for accessibility |
| **Prerequisites** | Modal dialog is open |
| **Test Steps** | 1. Open modal by triggering action<br>2. Press Tab key repeatedly to navigate through modal buttons<br>3. Verify Tab cycles through modal elements only<br>4. Verify focus does not move to background content<br>5. Verify focus returns to trigger button after modal closes |
| **Test Criteria** | ✓ Tab focus stays within modal<br>✓ Focus cycles through all modal elements<br>✓ Focus does not move to background<br>✓ Focus is restored to trigger element on close<br>✓ Modal is accessible via keyboard alone |

---

## Test Execution Notes

### Priority Levels

- Critical: Navigation, login, core workflows (events, rewards)
- High: Visual feedback, responsive design, error handling
- Medium: Cross-browser, accessibility, edge cases
- Low: Performance optimization, advanced features

### Test Environment

- Browser: Chrome
- Devices: Desktop. Used devtools to emulate iPhones
- Database: Test environment with sample data