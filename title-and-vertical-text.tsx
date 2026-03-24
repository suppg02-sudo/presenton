const layoutId = "title-and-vertical-text";
const layoutName = "Title and Vertical Text";
const layoutDescription = "A slide with title on the left and vertical text on the right";

const Schema = z.object({
  verticalText: z.string().min(1).default("Vertical Text"),
  title: z.string().min(1).default("Slide Title"),
  content: z.string().default("Body content goes here")
});

const dynamicSlideLayout = ({ data }) => {
  const {
    verticalText = 'Vertical Text',
    title = 'Slide Title',
    content = 'Body content goes here'
  } = data || {};

  const containerStyle = {
    display: 'flex',
    width: '100%',
    height: '100vh',
    backgroundColor: '#FFFFFF',
    fontFamily: 'Calibri, sans-serif',
    margin: 0,
    padding: 0
  };

  const sidebarStyle = {
    backgroundColor: '#8F1A95',
    width: '60px',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    padding: '20px 0',
    flexShrink: 0
  };

  const verticalTextStyle = {
    color: '#FFFFFF',
    fontFamily: 'Calibri Light, sans-serif',
    fontSize: '18px',
    fontWeight: 300,
    writingMode: 'vertical-rl',
    transform: 'rotate(180deg)',
    textAlign: 'center',
    margin: 0,
    padding: '10px',
    lineHeight: 1.4,
    wordBreak: 'break-word',
    maxHeight: '100%',
    overflow: 'hidden'
  };

  const contentAreaStyle = {
    flex: 1,
    display: 'flex',
    flexDirection: 'column',
    justifyContent: 'center',
    padding: '40px',
    backgroundColor: '#FFFFFF'
  };

  const titleStyle = {
    color: '#44546A',
    fontFamily: 'Calibri Light, sans-serif',
    fontSize: '48px',
    fontWeight: 300,
    margin: '0 0 30px 0',
    padding: 0,
    lineHeight: 1.2
  };

  const bodyStyle = {
    color: '#44546A',
    fontFamily: 'Calibri, sans-serif',
    fontSize: '18px',
    fontWeight: 400,
    margin: 0,
    padding: 0,
    lineHeight: 1.6
  };

  return (
    <div style={containerStyle} data-layout="title-and-vertical-text">
      <div style={sidebarStyle}>
        <p style={verticalTextStyle}>{verticalText}</p>
      </div>
      <div style={contentAreaStyle}>
        <h1 style={titleStyle}>{title}</h1>
        <p style={bodyStyle}>{content}</p>
      </div>
    </div>
  );
};

