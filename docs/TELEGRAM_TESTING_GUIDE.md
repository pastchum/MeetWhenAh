# Telegram Mini App Testing Guide

## Overview

This guide explains how to test your MeetWhenAh Telegram Mini App in different environments, from local development to production testing on iPhone.

## 🏠 Local Development Testing

### 1. Basic Development Setup
```bash
cd webapp
npm install
npm run dev
```

Your app will now be available at `http://localhost:3000` with:
- ✅ Telegram Web App environment mocked
- ✅ Telegram UI wrapper (header, footer, iPhone-like dimensions)
- ✅ All Telegram Web App APIs logged to console
- ✅ Dark theme matching Telegram's design

### 2. What You'll See
- **Telegram Header**: Back button, app title, menu button
- **Content Area**: Your app content in a scrollable area
- **Telegram Footer**: Main action button
- **iPhone Dimensions**: 414px max-width to simulate iPhone
- **Dark Theme**: Matches Telegram's dark theme

### 3. Console Logging
All Telegram Web App API calls are logged with `[TMA-mock]` prefix:
```
[TMA-mock] WebApp ready
[TMA-mock] Main button clicked
[TMA-mock] Data sent: {"event_name":"Test Event"}
```

## 📱 Telegram Test Environment

### 1. BotFather Setup
1. Message [@BotFather](https://t.me/botfather) on Telegram
2. Create a new bot: `/newbot`
3. Set bot name and username
4. Get your bot token

### 2. Mini App Setup
1. Message BotFather: `/newapp`
2. Select your bot
3. Set app title: "MeetWhenAh"
4. Set app short description
5. Upload app icon (512x512 PNG)
6. Get your Mini App URL

### 3. Development Testing
```bash
# Deploy your app to a public URL (Vercel, Netlify, etc.)
npm run build
# Deploy to your hosting platform
```

### 4. Test in Telegram
1. Open Telegram on your iPhone
2. Find your bot: `@your_bot_username`
3. Send `/start` to your bot
4. Click the "Start" button or any inline button that opens your Mini App
5. Your app will open in Telegram's Web App interface

## 🔧 Advanced Testing

### 1. Test Different Scenarios
- **Private Chat**: Test with individual users
- **Group Chat**: Test in group conversations
- **Channel**: Test when shared in channels
- **Inline Mode**: Test when shared as inline results

### 2. Test Different Devices
- **iPhone**: Primary testing device
- **Android**: Test on Android devices
- **Desktop**: Test in Telegram Desktop
- **Web**: Test in Telegram Web

### 3. Test Different Themes
- **Light Theme**: Set device to light mode
- **Dark Theme**: Set device to dark mode
- **System Theme**: Test with system theme changes

## 🚀 Production Testing

### 1. Deploy to Production
```bash
# Build for production
npm run build

# Deploy to your hosting platform
# Example with Vercel:
vercel --prod
```

### 2. Update BotFather
1. Message BotFather: `/myapps`
2. Select your app
3. Update the URL to your production domain
4. Test the production version

### 3. Real User Testing
- Share your bot with friends/family
- Test in real group conversations
- Gather feedback on usability
- Test on different network conditions

## 🐛 Debugging Tips

### 1. Console Debugging
```javascript
// Check if Telegram Web App is available
console.log('Telegram WebApp:', window.Telegram?.WebApp);

// Check user data
console.log('User:', window.Telegram?.WebApp?.initDataUnsafe?.user);

// Check theme
console.log('Theme:', window.Telegram?.WebApp?.themeParams);
```

### 2. Network Debugging
- Use browser dev tools to monitor network requests
- Check for CORS issues
- Verify API endpoints are working
- Monitor WebSocket connections if used

### 3. Performance Testing
- Test on slow network connections
- Monitor app load times
- Check memory usage
- Test with large datasets

## 📋 Testing Checklist

### Development Testing
- [ ] App loads without errors
- [ ] Telegram Web App APIs work
- [ ] UI matches Telegram design
- [ ] Responsive design works
- [ ] All features function correctly
- [ ] Console logs are helpful

### Production Testing
- [ ] App loads in Telegram
- [ ] All features work in Telegram
- [ ] Performance is acceptable
- [ ] No console errors
- [ ] Works on different devices
- [ ] Works with different themes

### User Experience Testing
- [ ] Intuitive navigation
- [ ] Clear call-to-actions
- [ ] Proper error handling
- [ ] Loading states
- [ ] Success feedback
- [ ] Accessibility features

## 🔗 Useful Resources

- [Telegram Mini Apps Documentation](https://core.telegram.org/bots/webapps)
- [Telegram Web App API Reference](https://core.telegram.org/bots/webapps#initializing-mini-apps)
- [BotFather Commands](https://t.me/botfather)
- [Telegram Test Environment](https://t.me/test)

## 🆘 Troubleshooting

### Common Issues
1. **App not loading**: Check deployment URL and BotFather settings
2. **API errors**: Verify your backend is accessible from Telegram
3. **Styling issues**: Ensure CSS works in Telegram's WebView
4. **Performance problems**: Optimize bundle size and loading times

### Getting Help
- Check Telegram's official documentation
- Join Telegram developer communities
- Review error logs and console output
- Test with minimal examples first 